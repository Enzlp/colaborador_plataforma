from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, generics, status
from .models import Author, MvIaConcept, MvLatamAuthor, Institution, Work, MvLatamIaAuthorConcept, Concept, MvRecommendationAuthorPool, WorkAuthorship
from .serializers import AuthorSerializer, RecommendationListSerializer, GetRecommendationsRequestSerializer, MvIaConceptSerializer, AuthorsAutocompleteSerializer, InstitutionSerializer, WorkSerializer
from recommender.hybrid_recommender import HybridRecommender
from rest_framework.views import APIView
from rest_framework.response import Response
import math
from recommender.content_based.queries import ContentBasedQueries

from django.db.models import Q, Subquery
from django.db.models import Func, Value
from django.db.models.fields import CharField
import re


class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    def get_queryset(self):
        queryset = Author.objects.all()

        author_id = self.request.query_params.get('id')
        if author_id:
            return queryset.filter(id=author_id)

        return Author.objects.all()[:50]
    
class InstitutionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer

    def get_queryset(self):
        queryset = Institution.objects.all()

        institution_id = self.request.query_params.get('id')
        if institution_id:
            return queryset.filter(id=institution_id)
        return
    
# View para works de un autor
class AuthorWorksView(APIView):
    def get(self, request, author_id: str):
        limit = int(request.query_params.get("limit", 100))
        concept_id = request.query_params.get("concept_id", None)

        
        if limit <= 0:
            return Response({"results": [], "count": 0})
        
        # Normalizar author_id
        if not author_id.startswith('https://'):
            author_id = f'https://openalex.org/{author_id}'
        
        try:
            author_obj = Author.objects.get(id=author_id)
        except Author.DoesNotExist:
            return Response({"results": [], "count": 0})
        
        # Query base
        base_qs = Work.objects.filter(
            authorships__author=author_obj
        )

        if concept_id:
            if not concept_id.startswith('https://'):
                concept_id = f'https://openalex.org/{concept_id}'
            
            base_qs = base_qs.filter(
                work_concepts__concept__id=concept_id
            )
        
        dedup_ids = (
            base_qs
            .order_by("id", "-publication_date")
            .distinct("id")
            .values("id")
        )
        
        # Ordenamiento real
        works_qs = (
            Work.objects
            .filter(id__in=dedup_ids)
            .order_by("-publication_date", "-id")[:limit]
        )
        
        serializer = WorkSerializer(works_qs, many=True)
        
        return Response({
            "results": serializer.data,
            #"count": works_qs.count() if works_qs else 0,
            "count": len(serializer.data)
        })
    
# Views autocompletado
def generar_patron_acronimo(query):
    """
    Convierte una cadena corta (ej: 'nlp') en un patrón de regex
    para buscar las iniciales de cada palabra (ej: 'N.*L.*P.*').
    """

    query = query.upper()
    
    pattern = '.*'.join(list(query))
    
    return pattern

class ConceptAutocomplete(generics.ListAPIView):
    serializer_class = MvIaConceptSerializer

    def get_queryset(self):
        query = self.request.GET.get('search', '')
        
        if not query:
            return MvIaConcept.objects.none()

        acronym_pattern = generar_patron_acronimo(query)
        filtro_normal = Q(display_name__istartswith=query)
        filtro_acronimo = Q(display_name__iregex=r'\y' + acronym_pattern)


        queryset = MvIaConcept.objects.filter(
            filtro_normal | filtro_acronimo
        ).distinct() 
        
        return queryset[:10]

DE_ACENTUADO = 'áéíóúÁÉÍÓÚñÑ'
A_NORMAL = 'aeiouAEIOUnN'

class AuthorsAutocompleteView(generics.ListAPIView):
    serializer_class = AuthorsAutocompleteSerializer

    def get_queryset(self):
        query = self.request.GET.get('search', '')
        
        if not query:
            return MvRecommendationAuthorPool.objects.none()
        
        columna_normalizada = Func(
            'display_name',
            Value(DE_ACENTUADO),
            Value(A_NORMAL),
            function='TRANSLATE',
            output_field=CharField()
        )

        termino_limpio = query.translate(str.maketrans(DE_ACENTUADO, A_NORMAL))

        return (
            MvRecommendationAuthorPool.objects
            .annotate(display_name_normalized=columna_normalizada)
            .filter(display_name_normalized__icontains=termino_limpio)
        )[:10]


class RecommendationViewSet(APIView):
    """
    API endpoint para obtener recomendaciones de autores
    basadas en conceptos de interés del usuario.
    """

    def post(self, request):
        input_serializer = GetRecommendationsRequestSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        validated_data = input_serializer.validated_data
        concept_vector = validated_data.get('concept_vector')
        author_id = validated_data.get('author_id')
        alpha = validated_data.get('alpha', 0.5)
        beta = validated_data.get('beta', 0.5)
        limit = validated_data.get('limit', 50)
        country_code = validated_data.get('country_code', '')
        order_by = validated_data.get('order_by', 'sim')

        # Inicializar cache CB
        ContentBasedQueries._initialize_cache()
        concept_to_index = ContentBasedQueries._cache['concept_to_index']


        AI_ID = "https://openalex.org/C154945302"
        DATA_SCIENCE_ID = "https://openalex.org/C2522767166"
        DATA_MINING_ID = "https://openalex.org/C124101348"

        SPECIFIC_SUBFIELDS = {
            "https://openalex.org/C204321447",  
            "https://openalex.org/C31972630",  
            "https://openalex.org/C28490314",   
        }

        # Si hay filtro por país, traemos más candidatos primero
        candidate_limit = 20000 if country_code else limit

        # Recomendaciones híbridas
        recommendations = HybridRecommender().get_recommendations(
            user_input=concept_vector,
            author_id=author_id,
            alpha=alpha,
            beta=beta,
            k=candidate_limit
        )

        if not recommendations:
            response_data = {'total_recommendations': 0, 'recommendations': []}
            return Response(
                RecommendationListSerializer(response_data).data,
                status=status.HTTP_200_OK
            )

        # Extraer scores
        top_author_ids = [aid for aid, _, _, _ in recommendations]
        hybrid_scores_dict = {aid: s for aid, s, _, _ in recommendations}
        cb_scores_dict = {aid: cb for aid, _, cb, _ in recommendations}
        cf_scores_dict = {aid: cf for aid, _, _, cf in recommendations}

        # FILTRO POR PAÍS
        if country_code:
            valid_author_ids = set(
                MvLatamAuthor.objects.filter(
                    id__in=top_author_ids,
                    country_code=country_code
                ).values_list('id', flat=True)
            )

            recommendations = [
                (aid, s, cb, cf)
                for aid, s, cb, cf in recommendations
                if aid in valid_author_ids
            ]

            if not recommendations:
                response_data = {'total_recommendations': 0, 'recommendations': []}
                return Response(
                    RecommendationListSerializer(response_data).data,
                    status=status.HTTP_200_OK
                )

        # Actualizar ids
        top_author_ids = [aid for aid, _, _, _ in recommendations]

        authors_dict = MvLatamAuthor.objects.filter(
            id__in=top_author_ids
        ).only(
            'id',
            'orcid',
            'display_name',
            'works_count',
            'cited_by_count',
            'country_code',
            'institution_name'
        ).in_bulk()

        # ORDENAMIENTO
        if order_by == 'works':
            recommendations = sorted(
                recommendations,
                key=lambda x: (
                    -(authors_dict.get(x[0]).works_count or 0),
                    -x[1]
                )
            )

        elif order_by == 'cites':
            recommendations = sorted(
                recommendations,
                key=lambda x: (
                    -(authors_dict.get(x[0]).cited_by_count or 0),
                    -x[1]
                )
            )

        # Límite final
        recommendations = recommendations[:limit]

        # Recalcular ids finales
        top_author_ids = [aid for aid, _, _, _ in recommendations]

        # Conceptos top
        concept_rows = MvLatamIaAuthorConcept.objects.filter(
            author_id__in=top_author_ids
        )

        all_concept_ids = set()
        top_concepts_temp = {}

        for row in concept_rows:
            concept_ids = row.concept_ids or []
            concept_tfs = row.concept_tfs or []

            total_tf = sum(concept_tfs)
            if total_tf == 0:
                continue

            tf_norm_scores = []

            for concept_id, raw_tf in zip(concept_ids, concept_tfs):

                # Solo conceptos del pool IA
                if concept_id not in concept_to_index:
                    continue

                # Excluir siempre IA y Data Science
                if concept_id == AI_ID or concept_id == DATA_SCIENCE_ID:
                    continue

                tf_norm = raw_tf / total_tf
                if tf_norm > 0:
                    tf_norm_scores.append((concept_id, tf_norm))

            if not tf_norm_scores:
                continue

            # Orden preliminar
            tf_norm_scores.sort(key=lambda x: x[1], reverse=True)

            # Detectar si hay sublíneas específicas
            has_specific = any(
                cid in SPECIFIC_SUBFIELDS
                for cid, _ in tf_norm_scores
            )

            final_pairs = []
            for cid, score in tf_norm_scores:
                # Data Mining solo si no hay sublíneas más específicas
                if cid == DATA_MINING_ID and has_specific:
                    continue
                final_pairs.append((cid, score))
                if len(final_pairs) == 3:
                    break

            top_concepts_temp[row.author_id] = final_pairs

            for cid, _ in final_pairs:
                all_concept_ids.add(cid)

        # Resolver nombres
        concept_objects = Concept.objects.filter(
            id__in=all_concept_ids
        ).only("id", "display_name")

        concept_name_map = {c.id: c.display_name for c in concept_objects}

        concepts_dict = {}
        for author_id, pairs in top_concepts_temp.items():
            concepts_dict[author_id] = [
                {
                    "concept_id": cid,
                    "score": float(score),
                    "display_name": concept_name_map.get(cid)
                }
                for cid, score in pairs
            ]


        author_data = []
        for aid in top_author_ids:
            author = authors_dict.get(aid)
            if not author:
                continue

            author_data.append({
                "author_id": aid,
                "orcid": author.orcid,
                "display_name": author.display_name,
                "country_code": author.country_code,
                "institution_name": author.institution_name,
                "similarity_score": float(hybrid_scores_dict[aid]),
                "cb_score": float(cb_scores_dict[aid]),
                "cf_score": float(cf_scores_dict[aid]),
                "works_count": author.works_count or 0,
                "cited_by_count": author.cited_by_count or 0,
                "top_concepts": concepts_dict.get(aid, [])
            })

        response_data = {
            "total_recommendations": len(author_data),
            "recommendations": author_data
        }

        return Response(
            RecommendationListSerializer(response_data).data,
            status=status.HTTP_200_OK
        )

class AuthorConceptsView(APIView):
    """
    GET /api/authors/<author_id>/concepts/
    Devuelve los conceptos asociados al autor
    """
    def get(self, request, author_id):
        author_prefix = "https://openalex.org/"
        concept_ids = (
            MvLatamIaAuthorConcept.objects
            .filter(author_id=f"{author_prefix}{author_id}")
            .values_list("concept_ids", flat=True)
            .first()
        )

        if concept_ids is None:
            return Response(
                {"error": "Autor no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )

        concepts = Concept.objects.filter(id__in=concept_ids).values("id", "display_name")

        return Response(list(concepts), status=status.HTTP_200_OK)

