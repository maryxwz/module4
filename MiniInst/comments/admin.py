from django.contrib import admin
from comments.models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "author",
        "post",
        "is_deleted",
        "created_at",
    )
    list_display_links = (
        "id",
        "author",
        "post",
    )
    list_filter = (
        "id",
        "author",
        "post",
        "is_deleted",
        "created_at",
    )
    search_fields = (
        "id",
        "author",
        "post",
        "is_deleted",
        "is_archived",
    )

