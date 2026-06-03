import os
import numpy as np
from scipy.sparse import load_npz
from implicit.nearest_neighbours import CosineRecommender

"""
Modelo Itemknn para recomendaciones basadas en filtrado colaborativo
- método que inicializa lectura de archivos en caché
- método que genera la lista de recomendaciones en tuplas id y score (normalizado min-max)
"""
class ItemKNNQueries:
    _cache = None

    @classmethod
    def _initialize_cache(cls):
        if cls._cache is not None:
            return

        files_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "files"
        )

        author_to_idx = np.load(
            os.path.join(files_dir, "author_to_idx.npy"),
            allow_pickle=True
        ).item()
        idx_to_author = np.load(
            os.path.join(files_dir, "idx_to_author.npy"),
            allow_pickle=True
        ).item()

        X_full = load_npz(os.path.join(files_dir, "X_full.npz")).tocsr()

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
        cls._initialize_cache()

        author_to_idx = cls._cache["author_to_idx"]
        idx_to_author = cls._cache["idx_to_author"]
        X_full = cls._cache["X_full"]
        model = cls._cache["model"]

        if author_id not in author_to_idx:
            print(f"Autor {author_id} no encontrado")
            return []

        author_idx = author_to_idx[author_id]

        if n_recs is None:
            n_recs = len(idx_to_author) - 1

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

        min_score = scores.min()
        max_score = scores.max()
        epsilon = 1e-8

        if (max_score - min_score) > epsilon:
            scores_norm = (scores - min_score) / (max_score - min_score)
        else:
            scores_norm = np.zeros_like(scores)

        recommendations = [
            (idx_to_author[idx], float(s_norm))
            for idx, s_norm in zip(ids, scores_norm)
        ]

        return recommendations
