from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.pagination import CustomPageNumberPagination
from api.serializers import CustomUserSerializer, FollowSerializer
from .models import Follow

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPageNumberPagination

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            data = {'user': user.id,
                    'author': author.id}
            serializer = FollowSerializer(author, data=data)
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subscription = get_object_or_404(Follow, user=user, author=author)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = FollowSerializer(paginated_queryset,
                                      many=True,
                                      context={'request': request})
        return self.get_paginated_response(serializer.data)
