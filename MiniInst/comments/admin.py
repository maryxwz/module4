from django.contrib import admin
from .models.comment import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "author",
        "get_related_object",
        "is_deleted",
        "created_at",
    )
    list_display_links = (
        "id",
        "author",
        "get_related_object",
    )
    list_filter = (
        "author",
        "is_deleted",
        "created_at",
    )
    search_fields = (
        "author__username",
        "text",
    )

    def get_related_object(self, obj):
        """Показує, до чого належить коментар"""
        if hasattr(obj.content_object, "title"):
            return f"Post: {obj.content_object.title}"
        elif hasattr(obj.content_object, "bio"):
            return f"Reels: {obj.content_object.author.username}"
        return str(obj.content_object)

    get_related_object.short_description = "Коментар до"

