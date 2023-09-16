 from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
 from rest_framework import filters

 from recipes.models import Tag, Ingredient,
 from .serializers import TagSerializer, IngredientSerializer


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
