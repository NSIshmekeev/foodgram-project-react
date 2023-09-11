from rest_framework.serializers import ModelSerializer, SerializerMethodField
from djoser.serializers import UserSerializer, UserCreateSerializer

from .users.models import User, Follow


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

# class FollowSerializer(ModelSerializer):
#     # recipes = SerializerMethodField()
#     # recipes_count = SerializerMethodField()
#     #
#     # def get_recipes(self, author):
#     #     re
#     #
#     # class Meta:

