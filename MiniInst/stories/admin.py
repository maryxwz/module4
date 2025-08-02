from django.contrib import admin
from stories.models import Story


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "author",
        "is_archived",
        "expires_at",
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
        "expires_at",
        "created_at",
    )
    search_fields = (
        "id",
        "author",
        "is_archived",
        "expires_at",
    )

