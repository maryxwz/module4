from django.contrib import admin
from posts.models import Post, Like


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "author",
        "caption",
        "is_archived",
        "created_at",
    )
    list_display_links = (
        "id",
        "author",
    )
    list_filter = (
        "id",
        "author",
        "is_archived",
        "created_at",
    )
    search_fields = (
        "id",
        "author",
        "caption",
        "is_archived",
    )


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "post",
        "created_at",
    )
    list_display_links = (
        "id",
        "user",
        "post",
    )
    list_filter = (
        "id",
        "user",
        "post",
        "created_at",
    )
    search_fields = (
        "id",
        "user",
        "post",
    )