from rest_framework import serializers
from .models import Author, MvIaConcept, MvLatamIaAuthorConcept, Institution, Work, MvRecommendationAuthorPool
class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = [
            "id",
            "orcid",
            "display_name",
            "display_name_alternatives",
            "works_count",
            "cited_by_count",
            "last_known_institution",
            "works_api_url",
            "updated_date"
        ]

class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = [
            "id",
            "display_name",
            "homepage_url",
            "country_code"
        ]

class WorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Work
        fields = [
            "id",
            "doi",
            "title" ,
            "display_name" ,
            "publication_year",
            "publication_date",
            "type" ,
            "cited_by_count",
            "is_retracted",
            "is_paratext",
            "language"
        ]

# Serializer autocompletado concepts
class MvIaConceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = MvIaConcept
        fields = [
            "id",
            "display_name"
        ]

# Serializer autocompletado de autores
class AuthorsAutocompleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MvRecommendationAuthorPool
        fields = [
            "author_id",
            "display_name",
        ]
# Serializers para recommendaciones
class ConceptScoreSerializer(serializers.Serializer):
    concept_id = serializers.CharField()
    score = serializers.FloatField()
    display_name = serializers.CharField(allow_null=True, required=False)

class RecommendationSerializer(serializers.Serializer):
    author_id = serializers.CharField()
    orcid = serializers.CharField()
    display_name = serializers.CharField()
    country_code = serializers.CharField(allow_null=True)
    institution_name = serializers.CharField(allow_null=True)
    similarity_score = serializers.FloatField()
    cb_score = serializers.FloatField()
    cf_score = serializers.FloatField()
    works_count = serializers.IntegerField()
    cited_by_count = serializers.IntegerField()
    top_concepts = ConceptScoreSerializer(many=True)

class RecommendationListSerializer(serializers.Serializer):
    total_recommendations = serializers.IntegerField()
    recommendations = RecommendationSerializer(many=True)
    
class ConceptInputSerializer(serializers.Serializer):
    """Valida cada concepto individualmente"""
    id = serializers.CharField(
        max_length=100,
        required=True,
        help_text="ID del concepto de OpenAlex (ej: C41008148)"
    )
    display_name = serializers.CharField(
        max_length=200,
        required=True,
        help_text="Nombre del concepto (ej: Machine Learning)"
    )


class GetRecommendationsRequestSerializer(serializers.Serializer):
    concept_vector = serializers.ListField(
        child=ConceptInputSerializer(),
        required=False,
        allow_empty=True,
        help_text="Lista de conceptos de interés del usuario (opcional)"
    )
    author_id = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="ID del autor para recomendaciones colaborativas (opcional)"
    )
    alpha = serializers.FloatField(
        required=False,
        default=0.5,
        help_text="Peso del modelo content-based (0 a 1)"
    )
    beta = serializers.FloatField(
        required=False,
        default=0.5,
        help_text="Peso del modelo collaborative filtering (0 a 1)"
    )
    limit = serializers.IntegerField(
        required=False,
        default=50
    )
    country_code = serializers.CharField(
        required=False,
        default='',
        allow_blank=True
    )
    order_by = serializers.ChoiceField( 
        choices=['sim', 'works', 'cites'],
        required=False,
        default='sim',
        help_text="Criterio de ordenamiento: 'sim' (similaridad), 'works' (número de trabajos), 'cites' (número de citas)"
    )
    
    def validate(self, data):
        concept_vector = data.get("concept_vector", [])
        author_id = data.get("author_id", "").strip()
        # Reglas: al menos uno debe existir
        if not concept_vector and not author_id:
            raise serializers.ValidationError(
                "Debes enviar al menos concept_vector o author_id."
            )
        return data
