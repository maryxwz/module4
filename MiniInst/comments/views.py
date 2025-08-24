from django.apps import apps
from django.shortcuts import get_object_or_404, redirect
from .forms import CommentForm

Post = apps.get_model('posts', 'Post')


def create_comment(request, post_id: int):
    if not request.user.is_authenticated:
        return redirect("login")

    post = get_object_or_404(Post, pk=post_id)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.post = post
            obj.author = request.user
            obj.save()

    return redirect(request.META.get("HTTP_REFERER") or "/")


