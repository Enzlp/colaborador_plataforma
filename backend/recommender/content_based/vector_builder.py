import os
import math
import pickle
import numpy as np
from scipy.sparse import lil_matrix, save_npz
from sklearn.preprocessing import normalize
from api.models import MvIaConcept, MvLatamIaAuthorConcept, MvRecommendationAuthorPool


def map_concepts(files_dir):
    """
    Crea un archivo con el mapeo de conceptos a índices
    """
    # --- Simulación de carga de conceptos si el modelo no está definido aquí ---
    try:
        # Intenta cargar el modelo MvIaConcept si está disponible
        concepts = MvIaConcept.objects.values_list("id", flat=True).order_by("id")
    except ImportError:
        print("ADVERTENCIA: MvIaConcept no encontrado. Usando conceptos simulados.")
        concepts = [f'C{i}' for i in range(1124)] # Simulación de 1124 conceptos
    # --------------------------------------------------------------------------
    
    concept_mapping = {concept_id: idx for idx, concept_id in enumerate(concepts)}
    file_path = os.path.join(files_dir, 'concept_mapping.pkl')
    with open(file_path, "wb") as f:
        pickle.dump(concept_mapping, f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"Mapeo de conceptos creado: {len(concept_mapping)} conceptos")


def train_model(files_dir):
    """
    Entrena el modelo usando:
    1) Term Frequency (TF) basada en conteo de papers.
    2) Ponderación por Inverse Document Frequency (IDF) suave.
    3) Normalización L2.
    """
    # Cargar mapping de conceptos
    concept_mapping_path = os.path.join(files_dir, "concept_mapping.pkl")
    with open(concept_mapping_path, 'rb') as f:
        concept_to_index = pickle.load(f)
    
    n_concepts = len(concept_to_index)
    
    # Cargar autores
    print("Cargando autores...")
    authors_data = list(MvRecommendationAuthorPool.objects.all().order_by('author_id'))
    n_authors = len(authors_data)

    
    print(f"Procesando {n_authors:,} autores con {n_concepts} conceptos...")
    
    # PASO 1: Construir TF (Term Frequency) y calcular DF (Document Frequency)
    matrix_tf = lil_matrix((n_authors, n_concepts), dtype=np.float32)
    author_ids = []
    author_work_counts = []
    
    # Para calcular DF (Document Frequency)
    concept_doc_freq = np.zeros(n_concepts, dtype=np.int32)
    
    print("Paso 1/3: Construyendo TF (Frecuencia Absoluta) y calculando DF...")
    for author_idx, author in enumerate(authors_data):
        author_ids.append(author.author_id)
        
        concept_ids = author.concept_ids or []
        concept_tfs = author.concept_tfs or []
        
        # Obtener cantidad de works (se mantiene por si se usa en metadata/otros)
        work_count = getattr(author, 'works_count', sum(concept_tfs)) 
        author_work_counts.append(work_count)
        
        # Marcar conceptos presentes para este autor (para DF)
        concepts_present = set()
        
        for i, concept_id in enumerate(concept_ids):
            if concept_id not in concept_to_index:
                continue
            
            concept_idx = concept_to_index[concept_id]
            
            # TF: Ahora es la frecuencia de papers (Conteo Absoluto)
            tf_value = float(concept_tfs[i]) if i < len(concept_tfs) else 0.0
            
            # Opcional: Aplicar Sublinear TF si se desea reducir el efecto de las frecuencias altas
            if tf_value > 0:
                tf_value = 1 + math.log(tf_value)
            
            matrix_tf[author_idx, concept_idx] = tf_value
            
            # Registrar concepto presente
            if tf_value > 0:
                 concepts_present.add(concept_idx)
        
        # Incrementar DF para conceptos presentes en este autor
        for concept_idx in concepts_present:
            concept_doc_freq[concept_idx] += 1
        
        if (author_idx + 1) % 10000 == 0:
            print(f"  Procesados {author_idx + 1:,}/{n_authors:,} autores...")
    
    # Convertir a CSR para operaciones eficientes
    matrix_tf = matrix_tf.tocsr()
    
    # PASO 2: Aplicar IDF (Inverse Document Frequency)
    print("Paso 2/3: Aplicando TF-IDF (con Smooth IDF)...")
    
    # Implementamos la fórmula Smooth IDF estándar: IDF(c) = log((N + 1) / (df(c) + 1)) + 1
    # Esto asegura robustez (no división por cero) y mejor ponderación
    idf = np.zeros(n_concepts, dtype=np.float32)
    N = n_authors # El número total de autores/documentos
    
    for concept_idx in range(n_concepts):
        df = concept_doc_freq[concept_idx]
        
        # Uso de Smooth IDF
        idf[concept_idx] = math.log((N + 1) / (df + 1)) + 1.0
    
    # Aplicar IDF a la matriz TF
    matrix_tfidf = matrix_tf.multiply(idf)
    
    # Liberar memoria
    del matrix_tf
    
    # PASO 3: Normalización L2 por filas (autores)
    print("Paso 3/3: Normalizando con L2...")
    matrix_final = normalize(matrix_tfidf, norm='l2', axis=1)
    
    # Guardar matriz y metadata
    print("Guardando archivos...")
    save_npz(os.path.join(files_dir, 'author_concept_matrix.npz'), matrix_final)
    
    # NUEVO: Guardar el vector IDF para su uso en la consulta (queries.py)
    np.save(
        os.path.join(files_dir, 'cb_idf_vector.npy'), 
        idf, 
        allow_pickle=False
    )
    
    # Guardar author_ids y work counts
    np.save(
        os.path.join(files_dir, 'cb_author_ids.npy'),
        np.array(author_ids, dtype=object),
        allow_pickle=True
    )
    
    np.save(os.path.join(files_dir, 'cb_author_work_counts.npy'), np.array(author_work_counts, dtype=np.int32))
    
    # Estadísticas (Resto del código de metadata...)
    work_counts_array = np.array(author_work_counts)
    metadata = {
        'n_concepts': n_concepts,
        'n_authors': n_authors,
        'mean_works': float(np.mean(work_counts_array)),
        'median_works': float(np.median(work_counts_array)),
        'min_works': int(np.min(work_counts_array)),
        'max_works': int(np.max(work_counts_array)),
        'sparsity': float(matrix_final.nnz / (n_authors * n_concepts)),
        'mean_idf': float(np.mean(idf[idf > 0])) if np.any(idf > 0) else 0.0,
        'max_idf': float(np.max(idf)),
        'min_idf': float(np.min(idf)) if np.any(idf) else 0.0, 
    }
    
    with open(os.path.join(files_dir, 'model_metadata.pkl'), 'wb') as f:
        pickle.dump(metadata, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    print("\n=== Entrenamiento completado ===")
    print(f"Total autores: {n_authors:,}")
    # ... (Resto de los printouts) ...
    print(f"Total conceptos: {n_concepts}")
    print(f"Promedio works/autor: {metadata['mean_works']:.2f}")
    print(f"Mediana works/autor: {metadata['median_works']:.2f}")
    print(f"Rango works: {metadata['min_works']} - {metadata['max_works']}")
    print(f"Sparsity: {metadata['sparsity']*100:.2f}%")
    print(f"IDF promedio (Smooth): {metadata['mean_idf']:.4f}")
    print(f"IDF rango (Smooth): [{metadata['min_idf']:.4f}, {metadata['max_idf']:.4f}]")
    print(f"Tamaño matriz: {matrix_final.data.nbytes / (1024**2):.2f} MB")