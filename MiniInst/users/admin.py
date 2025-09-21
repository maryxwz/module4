from django.contrib import admin
from users.models import CustomUser, Follow
from users.models import Block


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
        "is_banned",
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
        "is_banned",
    )
    search_fields = (
        'id',
        "username",
        "email",
    )

    def has_delete_permission(self, request, obj=None):
        if obj and (obj.is_staff or obj.is_superuser):
            return False
        return super().has_delete_permission(request, obj)

    def delete_queryset(self, request, queryset):

        only_users_queryset = queryset.exclude(is_staff=True, is_superuser=True)
        return super().delete_queryset(request, only_users_queryset)


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
@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "blocker",
        "blocked",
        "created_at"
    )
    search_fields = (
        "blocker__username",
        "blocked__username"
    )
    list_filter = (
        "created_at",
    )