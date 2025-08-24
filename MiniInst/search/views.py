from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth import get_user_model
import re


User = get_user_model()


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