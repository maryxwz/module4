from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from posts.models import Post, SavedPost


@login_required
def save_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    SavedPost.objects.get_or_create(user=request.user, post=post)
    return redirect("saved_posts")

@login_required
def saved_posts_view(request):
    saved_posts = SavedPost.objects.filter(user=request.user).select_related("post")
    return render(request, "saved_posts.html", {"saved_posts": saved_posts})
@login_required
@require_POST
def toggle_like(request, post_id):
    post = Post.objects.get(id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({
        'liked': liked,
        'likes_count': post.likes.count()
    })
