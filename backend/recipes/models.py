from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Модель тега"""

    name = models.CharField(
        'Название',
        unique=True,
        max_length=200
    )
    color = ColorField(
        'Цвет в формате Hex',
        format='hex',
        unique=True,
    )
    slug = models.SlugField(
        'Уникальный слаг',
        unique=True,
        max_length=200,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингердиента"""

    name = models.CharField(
        'Название ингредиента',
        max_length=200
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=50,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


# class IngredientInRecipe(models.Model):
#     """Модель количества ингредиентов в рецепте """
#     recipe = models.ForeignKey(
#         Recipe,
#         on_delete=models.CASCADE,
#         related_name='ingredient_list',
#         verbose_name='Рецепт',
#     )
#
#     ingredient = models.ForeignKey(
#         Ingredient,
#         on_delete=models.CASCADE,
#         related_name='ingredient_list',
#     )
#     amount = models.IntegerField(
#         'Количество',
#         validators=[MinValueValidator(1)],
#         default=1
#     )
#
#     class Meta:
#         verbose_name = 'Ингредиент рецепта'
#         verbose_name_plural = 'Ингредиенты рецепта'
#         constraints = [
#             models.UniqueConstraint(
#                 fields=('ingredient', 'amount'),
#                 name='unique_ingredient_in_recipe'),
#         ]
#
#     def __str__(self):
#         return f'{self.ingredient} - {self.amount}'


class Recipe(models.Model):
    """Модель рецепта"""
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        related_name='recipes',
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        'Название рецепта',
        max_length=200,
    )
    image = models.ImageField(
        'Изображение',
        blank=True,
        upload_to='recipes/images',
    )
    text = models.TextField(
        'Описание рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='Ингредиенты в рецепте',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes',
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления, мин.',
        validators=[
            MinValueValidator(1, message='Мин. время приготовления 1 минута')
        ],
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """Модель количества ингредиентов в рецепте """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_list',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_list',
    )
    amount = models.IntegerField(
        'Количество',
        validators=[MinValueValidator(1)],
        default=1
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='unique_ingredient_in_recipe'),
        ]

    def __str__(self):
        return f'{self.recipe} - {self.ingredient} - {self.amount}'


class Favourite(models.Model):
    """Модель избранного рецепта"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favourites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='favourites'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='favourites_for_user'),
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в избранные рецепты'


class ShoppingList(models.Model):
    """Модель списка покупок"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_list',

    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shopping_list'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='shopping_list'),
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в список покупок'
