from django.contrib import admin

from .models import User, Follow

class UserAdmin(admin.ModelAdmin):
    """Управление пользователем"""

    list_display = ('id', 'username', 'firt_name', 'last_name',
                    'email')
    list_display_links = ('id', 'username')
    list_filter = ('email', 'username')


class FollowAdmin(admin.ModelAdmin):
    """Управление подписками на автора"""

    list_display = ('id', 'user', 'following')
    search_fields = ('user',)


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
