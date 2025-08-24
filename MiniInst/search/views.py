from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.apps import apps
import re


User = get_user_model()
Follow = apps.get_model('users', 'Follow')
Post = apps.get_model('posts', 'Post')


def search_view(request):
    q = (request.GET.get("q") or "").strip()

    exact_user = None
    suggestions = []

    hashtag_query = None
    hashtag_posts = []

    if q:
        try:
            exact_user = User.objects.get(username__iexact=q)
        except User.DoesNotExist:
            exact_user = None

        user_qs = User.objects.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q)
        ).distinct().order_by('username')

        if exact_user:
            user_qs = user_qs.exclude(pk=exact_user.pk)
        suggestions = list(user_qs[:10])

        if q.startswith("#") and len(q) > 1:
            hashtag_query = q
            qs = Post.objects.filter(caption__icontains=hashtag_query).select_related("author")
            tag_escaped = re.escape(hashtag_query)
            pattern = re.compile(rf"(^|[^\w#]){tag_escaped}(\b|$)", re.IGNORECASE)

            hashtag_posts = [p for p in qs if (p.caption and pattern.search(p.caption))]

    context = {
        "q": q,
        "exact_user": exact_user,
        "suggestions": suggestions,
        "hashtag_query": hashtag_query,
        "hashtag_posts": hashtag_posts,
    }
    return render(request, "search/search.html", context)


def profile_public_view(request, username: str):
    target = get_object_or_404(User, username=username)
    is_private = getattr(target, "is_private", False)

    allowed = True
    if is_private:
        allowed = False
        if request.user.is_authenticated:
            allowed = Follow.objects.filter(
                follower=request.user,
                following=target
            ).exists()

    context = {
        "target": target,
        "is_private": is_private,
        "allowed": allowed,
    }
    return render(request, "search/profile_public.html", context)


