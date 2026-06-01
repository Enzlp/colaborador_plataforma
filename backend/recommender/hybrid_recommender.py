# Contenido de recommender/hybrid_recommender.py (Modificado)

from recommender.content_based.queries import ContentBasedQueries
from recommender.matrix_factorization.queries import MFQueries
from recommender.ItemKNN.queries import ItemKNNQueries

class HybridRecommender:
    @staticmethod
    def get_recommendations(
        user_input=None,
        author_id=None,
        k=30,
        alpha=0.5,
        beta=0.5
    ):
        # Referencias directas a las clases (NO instancias)
        content = ContentBasedQueries
        colab = ItemKNNQueries

        # -----------------------------------------------------
        # SOLO CONTENT-BASED
        # -----------------------------------------------------
        if user_input and not author_id:
            recs = content.get_recommendations(user_input=user_input)
            formatted = [(aid, cb_score, cb_score, 0.0) for aid, cb_score in recs]
            return formatted[:k]

        # -----------------------------------------------------
        # SOLO COLLABORATIVE
        # -----------------------------------------------------
        if author_id and not user_input:
            recs = colab.get_recommendations(author_id=author_id)
            formatted = [(aid, cf_score, 0.0, cf_score) for aid, cf_score in recs]
            return formatted[:k]

        # Ninguna entrada
        if not user_input and not author_id:
            return []

        # -----------------------------------------------------
        # HÍBRIDO
        # -----------------------------------------------------
        recs_cb = content.get_recommendations(user_input=user_input)
        recs_cf = colab.get_recommendations(author_id=author_id)

        if len(recs_cf) == 0:
            formatted = [(aid, cb_score, cb_score, 0.0) for aid, cb_score in recs_cb]
            return formatted[:k]

        d_cb = {aid: cb_score for aid, cb_score in recs_cb}
        d_cf = {aid: cf_score for aid, cf_score in recs_cf}

        all_authors = set(d_cb.keys()) | set(d_cf.keys())

        fused = []
        for aid in all_authors:
            cb = d_cb.get(aid, 0.0)
            cf = d_cf.get(aid, 0.0)
            hybrid = alpha * cb + beta * cf
            fused.append((aid, hybrid, cb, cf))

        fused.sort(key=lambda x: x[1], reverse=True)
        return fused[:k]
