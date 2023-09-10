from django.contrib import admin

from .models import (Tag, Ingredient, IngredinetInRecipe,
                     Recipe)

class TagAdmin(admin.ModelAdmin):
    """Управление тегами"""

    list_display = ('name', 'color', 'slug')
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)


class IngredientAdmin(admin.ModelAdmin):
    """Управление тегами"""

    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


class RecipesAdmin(admin.ModelAdmin):
    """Управление рецептами"""

    list_display = ('name', 'author')
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('author', 'name', 'tags')


class IngredientInRecipeAdmin(admin.ModelAdmin):
    """Управление ингредиентами в рецепте"""

    list_display = ('ingredient', 'count')
    list_filter = ('ingredient',)


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipesAdmin)
admin.site.register(IngredinetInRecipe, IngredientInRecipeAdmin)

