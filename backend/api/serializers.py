from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework.exceptions import ValidationError
from rest_framework import status
from djoser.serializers import UserSerializer, UserCreateSerializer

from users.models import User, Follow
from recipes.models import Recipe


class MyUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD, 'password'
        )


class MyUserSerializer(UserSerializer):
    is_subscribe = SerializerMethodField(read_only=True)

    def get_is_subscribe(self, author):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=author).exists()

    class Meta:
        model = User
        fields = ((User.USERNAME_FIELD, 'id')
                  + tuple(User.REQUIRED_FIELDS) + ('is_subscribe',))


class ShortRecipeSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(ModelSerializer):
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        fields = MyUserSerializer.Meta.fields + ('recipes', 'recipes_count')
        read_only_feilds = ('email', 'recipes')

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
