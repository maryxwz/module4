import base64
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from posts.models import Post, Like
from users.models import CustomUser, Follow
from .models.post import SavedPost, Repost
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post
from .forms import PostForm


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


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk, is_archived=False)
    return render(request, "posts/post_detail.html", {"post": post})


@login_required
def post_create(request):
    if request.method == "POST":
        edited_image = request.POST.get("edited_image")

        if edited_image:
            format, imgstr = edited_image.split(';base64,')
            ext = format.split('/')[-1]
            file = ContentFile(base64.b64decode(imgstr), name=f"post_{request.user.id}.{ext}")

            form = PostForm(request.POST, {'image': file})
            if form.is_valid():
                form.instance.author = request.user
                form.save()
                return redirect("/")
        else:
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                form.instance.author = request.user
                form.save()
                return redirect("/")
    else:
        form = PostForm()

    return render(request, "posts/post_form.html", {"form": form})


@login_required
def post_update(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect("posts:post_detail", pk=pk)
    else:
        form = PostForm(instance=post)

    return render(
        request,
        "posts/post_form.html",
        {
            "form": form,
            "user": request.user,
        }
    )


def post_archive(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    post.is_archived = True
    post.save()
    return redirect("post_list")


@login_required
def repost_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    repost, created = Repost.objects.get_or_create(user=request.user, post=post)
    if created:
        return JsonResponse({"status": "reposted"})
    else:
        repost.delete()
        return JsonResponse({"status": "unreposted"})


@login_required
def user_reposts(request, username):
    profile_user = get_object_or_404(CustomUser, username=username)

    reposts = Repost.objects.filter(
        user=profile_user
    ).select_related("post", "post__author")

    return render(
        request,
        "posts/user_reposts.html",
        {"reposts": reposts, "profile_user": profile_user}
    )


@login_required
def friends_reposts(request):
    friends_ids = Follow.objects.filter(
        follower=request.user
    ).values_list("following_id", flat=True)

    reposts = Repost.objects.filter(
        user__in=friends_ids
    ).select_related("post", "post__author", "user")

    return render(
        request,
        "posts/friends_reposts.html",
        {"reposts": reposts}
    )

