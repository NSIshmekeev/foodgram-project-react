from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet

from api.serializeres import MyUserSerializer

User = get_user_model()


class MyUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = MyUserSerializer


