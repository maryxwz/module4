from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.apps import apps
import re

User = get_user_model()
Follow = apps.get_model('users', 'Follow')


def search_view(request):
    q = (request.GET.get("q") or "").strip()
    exact_user = None
    suggestions = []

    if q:
        username = q.lstrip("@")
        exact_user = User.objects.filter(username__iexact=username).first()

        tokens = [t for t in re.split(r"\s+", q) if t]
        qs = User.objects.all()
        for t in tokens:
            qs = qs.filter(
                Q(username__icontains=t) |
                Q(first_name__icontains=t) |
                Q(last_name__icontains=t)
            )
        if exact_user:
            qs = qs.exclude(pk=exact_user.pk)
        suggestions = qs.order_by("username")[:20]

    return render(
        request,
        "search/search.html",
        {"q": q, "exact_user": exact_user, "suggestions": suggestions},
    )


def profile_public_view(request, username: str):
    target = get_object_or_404(User, username=username)
    is_private = getattr(target, "is_private", False)

    if request.user.is_authenticated and request.user.pk == target.pk:
        allowed = True
    else:
        if not is_private:
            allowed = True
        else:
            allowed = False
            if request.user.is_authenticated:
                allowed = Follow.objects.filter(follower=request.user, following=target).exists()

    context = {
        "target": target,
        "is_private": is_private,
        "allowed": allowed,
    }
    return render(request, "search/profile_public.html", context)

