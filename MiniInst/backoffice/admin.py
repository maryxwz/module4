from django.contrib import admin
from backoffice.models import UserReport


@admin.register(UserReport)
class UserReportAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "author",
        "description",
        "created_at",
    )
    list_display_links = (
        "id",
        "author",
    )
    list_filter = (
        "id",
        "author",
        "created_at",
    )
    search_fields = (
        "id",
        "author",
    )

