from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import (Favourite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingList, Tag)
from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPageNumberPagination
from .permissions import IsAuthorAdminOrReadOnly
from .serializers import (IngredientSerializer, RecipeCreateUpdateSerializer,
                          RecipeReadSerializer, ShortRecipeSerializer,
                          TagSerializer)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


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

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        if user.is_authenticated:
            if not Favourite.objects.filter(
                    user=user,
                    recipe=recipe
            ).exists():
                Favourite.objects.create(
                    user=user,
                    recipe=recipe
                )
                serializer = ShortRecipeSerializer(
                    recipe,
                    context={'request': request}
                )
                return Response(serializer.data)
            return Response(
                'Рецепт уже в избранном',
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            'Требуется авторизация',
            status=status.HTTP_401_UNAUTHORIZED
        )

    @favorite.mapping.delete
    def remove_favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        if user.is_authenticated:
            favorite = Favourite.objects.filter(
                user=user, recipe=recipe)
            if favorite.exists():
                favorite.delete()
                return Response('Удален из избранного')
            return Response(
                'Рецепта нет в избранном',
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            'Необходма авторизация',
            status=status.HTTP_401_UNAUTHORIZED
        )

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if ShoppingList.objects.filter(user=request.user,
                                       recipe=recipe).exists():
            return Response(
                {'errors': 'УЖе находится в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )
        ShoppingList.objects.create(user=request.user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe, many=False)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        get_object_or_404(ShoppingList, user=request.user,
                          recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        buy_list = IngredientInRecipe.objects.filter(
            recipe__shopping_list__user=user).values(
            'ingredient__name', 'ingredient__measurement_unit').annotate(
            total_number=Sum('amount')
        )
        text = 'Список покупок \n'
        for item in buy_list:
            amount = item['total_number']
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
