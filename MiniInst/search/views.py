from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth import get_user_model
import re

User = get_user_model()

def search_view(request):
    q_raw = (request.GET.get("q") or "").strip()

    exact_user = None
    suggestions = []
    hashtag_query = None
    hashtag_posts = []

    if q_raw:
        q = q_raw.strip()
        if q.startswith("@"):
            q = q[1:].strip()

        if q:
            try:
                exact_user = User.objects.get(username__iexact=q)
            except User.DoesNotExist:
                exact_user = None

            user_qs = User.objects.filter(
                Q(username__icontains=q) |
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q)
            ).order_by("username").distinct()

            if exact_user:
                user_qs = user_qs.exclude(pk=exact_user.pk)

            suggestions = list(user_qs[:10])

        if q_raw.startswith("#") and len(q_raw) > 1:
            hashtag_query = q_raw
            try:
                from posts.models.post import Post
            except Exception:
                Post = None

            if Post is not None:
                tag_escaped = re.escape(hashtag_query)
                pattern = re.compile(rf"(^|[^\w#]){tag_escaped}(\b|$)", re.IGNORECASE)
                qs = Post.objects.select_related("author").all()
                hashtag_posts = [
                    p for p in qs
                    if p.caption and pattern.search(p.caption)
                ]

    context = {
        "q": q_raw,
        "exact_user": exact_user,
        "suggestions": suggestions,
        "hashtag_query": hashtag_query,
        "hashtag_posts": hashtag_posts,
    }
    return render(request, "search/search.html", context)