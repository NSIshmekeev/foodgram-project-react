from rest_framework.serializers import (ModelSerializer,
                                        SerializerMethodField,
                                        ReadOnlyField, IntegerField,
                                        PrimaryKeyRelatedField)
from rest_framework.exceptions import ValidationError
from rest_framework import status
from djoser.serializers import UserSerializer, UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from django.shortcuts import get_object_or_404

from users.models import User, Follow
from recipes.models import (Recipe, Tag, Ingredient, IngredientInRecipe,
                            Favourite, ShoppingList)


class MyUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'password')


class MyUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=author).exists()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'is_subscribed')


class ShortRecipeSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(MyUserSerializer):
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'is_subscribed', 'recipes', 'recipes_count')

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Follow.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='Вы уже подписаны',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail='Невозможно подписаться на самого себя',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes(self, author):
        recipes = author.recipes.all()
        request = self.context.get('request')
        if 'recipes_limit' in request.GET:
            recipes = recipes[:int(request.GET['recipes_limit'])]
        serializer = ShortRecipeSerializer(recipes, many=True,
                                           read_only=True)
        return serializer.data

    def get_recipes_count(self, author):
        return author.recipes.count()


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(ModelSerializer):
    id = ReadOnlyField(source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientInRecipeCreateSerializer(ModelSerializer):
    id = IntegerField(write_only=True)
    amount = IntegerField(required=True)
    name = SerializerMethodField()
    measurement_unit = SerializerMethodField()

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount', 'name', 'measurement_unit')

    def get_measurement_unit(self, ingredient):
        measurement_unit = ingredient.ingredient.measurement_unit
        return measurement_unit

    def get_name(self, ingredient):
        name = ingredient.ingredient.name
        return name


class RecipeReadSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = MyUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(many=True)
    image = Base64ImageField()
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, recipe):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favourite.objects.filter(user=user, recipe=recipe)

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingList.objects.filter(recipe=recipe).exists()


class RecipeCreateUpdateSerializer(ModelSerializer):
    tags = PrimaryKeyRelatedField(required=True, many=True, queryset=Tag.objects.all())
    author = MyUserSerializer(read_only=True)
    ingredients = IngredientInRecipeCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'tags', 'ingredients',
                  'image', 'text', 'cooking_time')

    def validate_tags(self, value):
        if not value:
            return ValidationError(
                detail='Нужно выбрать хотя бы один тег!',
                code=status.HTTP_400_BAD_REQUEST
            )
        tag_set = set(value)
        if len(value) != len(tag_set):
            return ValidationError(
                detail='Теги не уникальны',
                code=status.HTTP_400_BAD_REQUEST
            )
        return value

    def validate_ingredients(self, value):
        if not value:
            return ValidationError(
                detail='Нужно чтобы был хотя-бы один игредиент',
                code=status.HTTP_400_BAD_REQUEST
            )
        ingredients = [item['id'] for item in value]
        for ingredient in ingredients:
            if ingredients.count(ingredient) > 1:
                raise ValidationError(
                    detail='У рецепта не может быть два одинаковых ингредиента.',
                    code=status.HTTP_400_BAD_REQUEST
                )
        return value

    def create_ingredients_amounts(self, ingredients, recipe):
        for ingredient in ingredients:
            ing, _ = IngredientInRecipe.objects.get_or_create(
                ingredient=get_object_or_404(
                    Ingredient.objects.filter(id=ingredient['id'])
                ),
                amount=ingredient['amount'],
            )
            recipe.ingredients.add(ing.id)

    def create(self, validated_data):
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            **validated_data
        )
        recipe.tags.set(tags)
        self.create_ingredients_amounts(recipe=recipe,
                                        ingredients=ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients')
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients_amounts(recipe=instance,
                                        ingredients=ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance, context=context).data
