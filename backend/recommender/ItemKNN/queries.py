import os
import numpy as np
from scipy.sparse import load_npz
from implicit.nearest_neighbours import CosineRecommender

class ItemKNNQueries:
    # Cache estático a nivel de clase
    _cache = None

    @classmethod
    def _initialize_cache(cls):
        """Inicializa el cache cargando el modelo y la matriz sparse"""
        if cls._cache is not None:
            return

        files_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "files"
        )

        # 1. Cargar mapeos
        author_to_idx = np.load(
            os.path.join(files_dir, "author_to_idx.npy"),
            allow_pickle=True
        ).item()
        idx_to_author = np.load(
            os.path.join(files_dir, "idx_to_author.npy"),
            allow_pickle=True
        ).item()

        # 2. Cargar Matriz de Interacciones
        X_full = load_npz(os.path.join(files_dir, "X_full.npz")).tocsr()

        # 3. Cargar el modelo correctamente
        # El método load es un classmethod, devuelve la instancia cargada.
        model_path = os.path.join(files_dir, "itemknn_best.npz")
        model = CosineRecommender.load(model_path)

        cls._cache = {
            "author_to_idx": author_to_idx,
            "idx_to_author": idx_to_author,
            "X_full": X_full,
            "model": model,
        }

    @classmethod
    def get_recommendations(cls, author_id, n_recs=None):
        # Inicializar cache
        cls._initialize_cache()

        author_to_idx = cls._cache["author_to_idx"]
        idx_to_author = cls._cache["idx_to_author"]
        X_full = cls._cache["X_full"]
        model = cls._cache["model"]

        if author_id not in author_to_idx:
            print(f"Autor {author_id} no encontrado")
            return []

        author_idx = author_to_idx[author_id]

        # Si no se especifica n_recs, intentamos traer a todos para el sorting global
        if n_recs is None:
            n_recs = len(idx_to_author) - 1

        # 🔹 Obtener recomendaciones de Implicit
        # recommend() devuelve IDs y scores (ya filtrando los que el autor ya conoce)
        ids, scores = model.recommend(
            userid=author_idx,
            user_items=X_full[author_idx],
            N=n_recs,
            filter_already_liked_items=True,
        )

        # Quita el autor consultado
        mask = ids != author_idx
        ids = ids[mask][:n_recs]
        scores = scores[mask][:n_recs]

        if len(scores) == 0:
            return []

        # 🔹 Normalización Min-Max (Score de Fusión)
        min_score = scores.min()
        max_score = scores.max()
        epsilon = 1e-8

        if (max_score - min_score) > epsilon:
            scores_norm = (scores - min_score) / (max_score - min_score)
        else:
            scores_norm = np.zeros_like(scores)

        # Construir lista de recomendaciones
        recommendations = [
            (idx_to_author[idx], float(s_norm))
            for idx, s_norm in zip(ids, scores_norm)
        ]

        return recommendations
