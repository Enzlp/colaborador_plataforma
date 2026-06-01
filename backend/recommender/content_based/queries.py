import os
import pickle
import numpy as np
from scipy.sparse import lil_matrix, load_npz
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize


class ContentBasedQueries:
    # Cache estático a nivel de clase
    _cache = None
    
    @classmethod
    def _initialize_cache(cls):
        """Inicializa el cache una sola vez"""
        if cls._cache is not None:
            return
        
        models_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "files"
        )
        
        # Cargar archivos
        with open(os.path.join(models_dir, 'concept_mapping.pkl'), 'rb') as f:
            concept_to_index = pickle.load(f)
        
        author_matrix = load_npz(os.path.join(models_dir, 'author_concept_matrix.npz'))
        author_ids = np.load(os.path.join(models_dir, 'cb_author_ids.npy'), allow_pickle=True)
        
        try:
            author_work_counts = np.load(os.path.join(models_dir, 'cb_author_work_counts.npy'))
        except FileNotFoundError:
            author_work_counts = np.ones(len(author_ids), dtype=np.int32)
        
        # Cargar score priori
        try:
            author_prior = np.load(os.path.join(models_dir, 'cb_author_prior.npy'))
        except FileNotFoundError:
            author_prior = np.zeros(len(author_ids), dtype=np.float32)

        # NUEVO: Cargar el vector IDF
        try:
            idf_vector = np.load(os.path.join(models_dir, 'cb_idf_vector.npy'))
        except FileNotFoundError:
            print("ADVERTENCIA: Archivo IDF no encontrado. Usando vector de unos (IDF=1).")
            # Si IDF no existe, usamos un vector de 1s para evitar errores de multiplicación.
            idf_vector = np.ones(len(concept_to_index), dtype=np.float32) 

        cls._cache = {
            'concept_to_index': concept_to_index,
            'author_matrix': author_matrix,
            'author_ids': author_ids,
            'author_work_counts': author_work_counts,
            'author_prior': author_prior,
            'n_concepts': len(concept_to_index),
            'idf_vector': idf_vector # Añadir IDF al caché
        }

    
    @staticmethod
    def create_user_vector(user_concepts, n_concepts, concepts_ids, idf_vector):
        """Método para crear el vector de conceptos del usuario con TF-IDF y L2."""
        user_vector = lil_matrix((1, n_concepts), dtype=np.float32)
        indices_to_process = []
        
        # PASO 1: Creación del TF (BoW = 1.0)
        for concept in user_concepts:
            concept_id = concept['id']
            if concept_id not in concepts_ids:
                continue
            concept_idx = concepts_ids[concept_id]
            user_vector[0, concept_idx] = 1.0  # TF es 1.0 (presencia)
            indices_to_process.append(concept_idx)
        
        user_vector = user_vector.tocsr()
        
        # PASO 2: Aplicar IDF (Ponderación de Rareza)
        if len(indices_to_process) > 0:
            # Crea un vector auxiliar con los valores de IDF solo en las posiciones presentes
            user_idf_weights = np.zeros(n_concepts, dtype=np.float32)
            user_idf_weights[indices_to_process] = idf_vector[indices_to_process]
            
            # Aplicar la ponderación TF-IDF: TF (1.0) * IDF
            user_vector_tfidf = user_vector.multiply(user_idf_weights)
        else:
            # Si el vector está vacío, no se aplica IDF y se mantiene (será un vector de ceros)
            user_vector_tfidf = user_vector
        
        # PASO 3: Normalizar L2
        # La L2 ahora normaliza el vector TF-IDF del usuario
        user_vector_final = normalize(user_vector_tfidf, norm='l2', axis=1)
        
        return user_vector_final
    
    @staticmethod
    def apply_bayesian_smoothing(similarities, work_counts, confidence_param=1.0):
        """
        Bayesian smoothing por AUTOR:
        adjusted_score = (C * m_author + n * sim) / (C + n)
        """

        similarities = np.array(similarities, dtype=float)
        work_counts = np.array(work_counts, dtype=float)
        m = np.mean(similarities)

        adjusted_scores = (
            confidence_param * m +
            work_counts * similarities
        ) / (confidence_param + work_counts)

        return adjusted_scores

    
    @classmethod
    def get_recommendations(cls, user_input):
        """
        Retorna TODOS los autores ordenados por similitud (sin threshold ni top_k),
        aplicando Normalización Gaussiana al score y Min-Max para el score de fusión.
        
        Args:
            user_input: Lista de conceptos del usuario con formato:
                    [{'id': concept_id}, ...]
        
        Returns:
            Lista de tuplas (author_id, score_min_max, z_score) ordenadas descendente
        """ # <--- Se modifica la documentación para reflejar los 3 valores.
        
        # Inicializar cache si es necesario
        cls._initialize_cache()
        
        concept_to_index = cls._cache['concept_to_index']
        author_matrix = cls._cache['author_matrix']
        author_ids = cls._cache['author_ids']
        n_concepts = cls._cache['n_concepts']
        idf_vector = cls._cache['idf_vector'] # Obtener el vector IDF del caché
        
        # Crear vector de usuario TF-IDF normalizado (L2)
        user_vector = cls.create_user_vector(
            user_input, 
            n_concepts, 
            concept_to_index, 
            idf_vector # Pasar el vector IDF
        )
        
        # Calcular similitud coseno directamente
        similarities = cosine_similarity(user_vector, author_matrix)[0]


        # Aplicar Bayesian Smoothing usando score_prior (Comentado, pero disponible)
        similarities = cls.apply_bayesian_smoothing(
             similarities,
             cls._cache['author_work_counts'],
             confidence_param=10.0
        )


        
        epsilon = 1e-8

        # Normalización min-max para posicion relativa
        min_sim = similarities.min()
        max_sim = similarities.max()
        if (max_sim - min_sim) > epsilon:
            similarities_norm = (similarities - min_sim) / (max_sim - min_sim)
        else:
            # Caso para evitar división por cero (si todos los scores son iguales)
            similarities_norm = np.zeros_like(similarities)
        
        #K_SIM_SCALER = 5.0
        #center_point_sim = np.median(similarities)
        #similarities_centered = similarities - center_point_sim
        #similarities_norm = 1.0 / (1.0 + np.exp(-K_SIM_SCALER * similarities_centered))
        
        # Ordenar autores por similitud descendentes
        # 💡 NOTA: Se mantiene la ordenación basada en Min-Max (similarities_norm)
        sorted_indices = np.argsort(-similarities_norm)
        sorted_author_ids = author_ids[sorted_indices]
        sorted_scores = similarities_norm[sorted_indices] # Min-Max score

        # Empaquetar resultados: (author_id, score_min_max, z_score)
        recommendations = [
            (author_id, float(score))
            for author_id, score in zip(sorted_author_ids, sorted_scores)
        ]
        
        return recommendations