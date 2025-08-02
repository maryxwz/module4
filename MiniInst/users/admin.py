from django.contrib import admin
from users.models import CustomUser, Follow


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "bio",
        "last_login",
        "date_joined",
        "is_private",
        "is_staff",
        "is_active",
    )
    list_display_links = (
        "id",
        "username",
        "email",
    )
    list_filter = (
        "id",
        "username",
        "email",
        "last_login",
        "date_joined",
        "is_private",
        "is_staff",
        "is_active",
    )
    search_fields = (
        'id',
        "username",
        "email",
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "follower",
        "following",
        "created_at",
    )
    list_display_links = (
        "id",
        "follower",
        "following",
    )
    list_filter = (
        "id",
        "follower",
        "following",
        "created_at",
    )
    search_fields = (
        "id",
        "follower",
        "following",
        "created_at",
    )
