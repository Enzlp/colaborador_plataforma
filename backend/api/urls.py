from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthorViewSet, RecommendationViewSet, ConceptAutocomplete, AuthorsAutocompleteView, InstitutionViewSet, AuthorWorksView, AuthorConceptsView

router = DefaultRouter()
router.register(r'authors', AuthorViewSet)
router.register(r'institution', InstitutionViewSet)

urlpatterns = [
    path('authors/<str:author_id>/works/', AuthorWorksView.as_view(), name='author-works'),
    path('authors/<str:author_id>/concepts/', AuthorConceptsView.as_view(), name='author-concepts'),
    path('', include(router.urls)),
    path('recommendation/', RecommendationViewSet.as_view(), name='recommendation'),
    path('concept/', ConceptAutocomplete.as_view(), name='concept-autocomplete'),
    path('authorsearch/', AuthorsAutocompleteView.as_view(), name='author-autocomplete'),
]
