from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from users.views import home_view, account_settings_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home_view, name="home"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("settings/", account_settings_view, name="settings"),
    path("backoffice/", include(("backoffice.urls", "backoffice"), namespace="backoffice")),
    path("direct/", include(("direct.urls", "direct"), namespace="direct")),
    path("search/", include(("search.urls", "search"), namespace="search")),
    path("stories/", include(("stories.urls", "stories"), namespace="stories")),
    path("users/", include(("users.urls", "users"), namespace="users")),
    path("posts/", include(("posts.urls", "posts"), namespace="posts")),
    path("comments/", include(("comments.urls", "comments"), namespace="comments")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)