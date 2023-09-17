from django.contrib.auth import get_user_model
from django_filters import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    is_favourited = filters.BooleanFilter(method='filter_is_favourited')
    is_in_shopping_list = filters.BooleanFilter(
        method='filter_is_in_shopping_list')

    class Meta:
        model = Recipe
        fields = ('tags', 'author',)

    def filter_is_favourited(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(favourites__user=user)
        return queryset

    def filter_is_in_shopping_list(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(shopping_list__user=user)
        return queryset
