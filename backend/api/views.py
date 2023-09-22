from django.db.models import Sum
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework import filters, status
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from recipes.models import (Tag, Ingredient, Recipe, Favourite, ShoppingList,
                            IngredientInRecipe)
from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeCreateUpdateSerializer,
                          ShortRecipeSerializer)
from .pagination import CustomPageNumberPagination
from .filters import RecipeFilter
from .permissions import IsAuthorAdminOrReadOnly


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = [IsAuthorAdminOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeCreateUpdateSerializer

    def add_to_list(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'errors': 'Рецепт уже добавлен!'},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from_list(self, model, user, pk):
        if not model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'errors': 'Рецепт уже удален!'},
                            status=status.HTTP_400_BAD_REQUEST)
        model.objects.filter(user=user, recipe__id=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_to_list(Favourite, request.user, pk)
        return self.delete_from_list(Favourite, request.user, pk)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_to_list(ShoppingList, request.user, pk)
        return self.delete_from_list(ShoppingList, request.user, pk)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        buy_list = IngredientInRecipe.objects.filter(
            recipe__shopping_list__user=user).values(
            'ingredient__name', 'ingredient__measurement_unit').annotate(
            amount=Sum('amount')
        )
        text = 'Список покупок \n'
        for item in buy_list:
            amount = item['amount']
            name = item['ingredient__name']
            measurement_unit = item['ingredient__measurement_unit']
            text += (
                f'{name} ({measurement_unit}), '
                f'{amount}\n'
            )
        response = HttpResponse(text, content_type="text/plain")
        response['Content-Disposition'] = (
            'attachment; filename=shopping-list.txt'
        )
        return response
