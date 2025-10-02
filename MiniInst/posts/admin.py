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
        "author",
        "is_archived",
        "created_at",
    )
    search_fields = (
        "caption",
        "author__username",
    )


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "related_object",
        "created_at",
    )
    list_display_links = (
        "id",
        "user",
        "related_object",
    )
    list_filter = (
        "user",
        "created_at",
    )
    search_fields = (
        "user__username",
    )

    def related_object(self, obj):
        """Показує, що саме лайкнули"""
        if hasattr(obj.content_object, "title"):
            return f"Post: {obj.content_object.title}"
        elif hasattr(obj.content_object, "bio"):
            return f"Reels: {obj.content_object.author.username} | {obj.content_object.created_at}"
        return str(obj.content_object)

    related_object.short_description = "Лайк до"
