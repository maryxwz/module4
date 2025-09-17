from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from users.forms import CustomUserCreationForm
from .models import Repost, Notification
from posts.models import Post


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def profile_view(request):
    return render(request, 'profile.html', {'user': request.user})


@login_required
def repost_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    repost, created = Repost.objects.get_or_create(user=request.user, post=post)
    if created:
        if post.author != request.user:
            Notification.objects.create(
                user=post.author,
                message=f"{request.user.username} зробив(ла) репост вашої публікації."
            )
        return JsonResponse({"status": "reposted"})
    else:
        repost.delete()
        return JsonResponse({"status": "unreposted"})


@login_required
def user_reposts(request, username):
    reposts = Repost.objects.filter(user__username=username).select_related("post", "post__author")
    return render(request, "user_reposts.html", {"reposts": reposts})
