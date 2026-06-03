import os
import pickle
import numpy as np
from scipy.sparse import lil_matrix, load_npz
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize


"""
Modelo Basado en Contenido
- inicializa lectura de archivos a un cache
- método que crea un vector de conceptos para cada usuario
- método aplica suavezimiento bayesiano en base a cantidad de publicaciones
- método que genera lista de recomendaciones en tuplas con el id y score
"""
class ContentBasedQueries:
    _cache = None
    @classmethod
    def _initialize_cache(cls):
        if cls._cache is not None:
            return
        
        models_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "files"
        )
        
        with open(os.path.join(models_dir, 'concept_mapping.pkl'), 'rb') as f:
            concept_to_index = pickle.load(f)
        
        author_matrix = load_npz(os.path.join(models_dir, 'author_concept_matrix.npz'))
        author_ids = np.load(os.path.join(models_dir, 'cb_author_ids.npy'), allow_pickle=True)
        
        try:
            author_work_counts = np.load(os.path.join(models_dir, 'cb_author_work_counts.npy'))
        except FileNotFoundError:
            author_work_counts = np.ones(len(author_ids), dtype=np.int32)
        
        try:
            author_prior = np.load(os.path.join(models_dir, 'cb_author_prior.npy'))
        except FileNotFoundError:
            author_prior = np.zeros(len(author_ids), dtype=np.float32)

        try:
            idf_vector = np.load(os.path.join(models_dir, 'cb_idf_vector.npy'))
        except FileNotFoundError:
            print("ADVERTENCIA: Archivo IDF no encontrado. Usando vector de unos (IDF=1).")
            idf_vector = np.ones(len(concept_to_index), dtype=np.float32) 

        cls._cache = {
            'concept_to_index': concept_to_index,
            'author_matrix': author_matrix,
            'author_ids': author_ids,
            'author_work_counts': author_work_counts,
            'author_prior': author_prior,
            'n_concepts': len(concept_to_index),
            'idf_vector': idf_vector 
        }

    
    @staticmethod
    def create_user_vector(user_concepts, n_concepts, concepts_ids, idf_vector):
        """Método para crear el vector de conceptos del usuario con TF-IDF y L2."""
        user_vector = lil_matrix((1, n_concepts), dtype=np.float32)
        indices_to_process = []
        
        for concept in user_concepts:
            concept_id = concept['id']
            if concept_id not in concepts_ids:
                continue
            concept_idx = concepts_ids[concept_id]
            user_vector[0, concept_idx] = 1.0  # TF es 1.0 (presencia)
            indices_to_process.append(concept_idx)
        
        user_vector = user_vector.tocsr()
        
        if len(indices_to_process) > 0:
            user_idf_weights = np.zeros(n_concepts, dtype=np.float32)
            user_idf_weights[indices_to_process] = idf_vector[indices_to_process]
            user_vector_tfidf = user_vector.multiply(user_idf_weights)
        else:
            user_vector_tfidf = user_vector
        
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
        cls._initialize_cache()
        
        concept_to_index = cls._cache['concept_to_index']
        author_matrix = cls._cache['author_matrix']
        author_ids = cls._cache['author_ids']
        n_concepts = cls._cache['n_concepts']
        idf_vector = cls._cache['idf_vector'] 

        user_vector = cls.create_user_vector(
            user_input, 
            n_concepts, 
            concept_to_index, 
            idf_vector 
        )

        similarities = cosine_similarity(user_vector, author_matrix)[0]

        similarities = cls.apply_bayesian_smoothing(
             similarities,
             cls._cache['author_work_counts'],
             confidence_param=10.0
        )
        
        epsilon = 1e-8
        # normalizacion min-max
        min_sim = similarities.min()
        max_sim = similarities.max()
        if (max_sim - min_sim) > epsilon:
            similarities_norm = (similarities - min_sim) / (max_sim - min_sim)
        else:
            similarities_norm = np.zeros_like(similarities)
        
        sorted_indices = np.argsort(-similarities_norm)
        sorted_author_ids = author_ids[sorted_indices]
        sorted_scores = similarities_norm[sorted_indices] 

        recommendations = [
            (author_id, float(score))
            for author_id, score in zip(sorted_author_ids, sorted_scores)
        ]
        
        return recommendations