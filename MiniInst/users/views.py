import random

from django.http.response import  Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model

from backoffice.forms import UserReportForm
from .forms import CustomUserCreationForm
from .models.follow import Follow
from .models.custom_user import CustomUser
from .models.block import Block
from posts.models.post import Post
from stories.models.story import Story



UserModel = get_user_model()


class CustomLoginView(auth_views.LoginView):
    def get_success_url(self):
        return reverse_lazy("profile", args=[self.request.user.username]) # щоб після логіну кидало на профіль цього юзера


def home_view(request):
    all_posts = list(Post.objects.all())
    for post in all_posts:
        if post.author.is_private:
            all_posts.remove(post)
    all_stories = [story for story in Story.objects.all() if not story.author.is_private and story.is_active()]
    if request.user.is_authenticated:
        blocked_ids = set(
            Block.objects.filter(blocker=request.user).values_list('blocked_id', flat=True)
        )
        blocked_me_ids = set(
            Block.objects.filter(blocked=request.user).values_list('blocker_id', flat=True)
        )
        banned_user_ids = blocked_ids.union(blocked_me_ids)
        if banned_user_ids:
            all_posts = all_posts.exclude(author_id__in=banned_user_ids)

    try:
        profile_user = CustomUser.objects.get(username=request.user.username)
    except ObjectDoesNotExist:
        return redirect('register')

    return render(request, 'home.html', {
        'profile_user': profile_user,
        'posts': all_posts,
        'stories': all_stories
    })


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile', username=request.user.username)
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(CustomUser, username=username)
    current_user = request.user
    if profile_user.is_banned:
        raise Http404("Профіль заблокован")
    # Перевірка чи поточний користувач підписаний на профіль
    is_following = Follow.objects.filter(
        follower=current_user,
        following=profile_user
    ).exists()

    is_blocked_by_me = Block.objects.filter(blocker=current_user, blocked=profile_user).exists()
    blocked_me = Block.objects.filter(blocker=profile_user, blocked=current_user).exists()
    blocked_between = is_blocked_by_me or blocked_me

    can_view_details = (
        current_user == profile_user or
        not profile_user.is_private or
        is_following
    )
    can_view_details = can_view_details and not blocked_between

    posts = []
    posts_count = 0
    if can_view_details:
        posts = profile_user.posts.all()
        posts_count = posts.count()

    followers_count = profile_user.followers.count() if can_view_details else 0
    following_count = profile_user.following.count() if can_view_details else 0

    if request.method == "POST":
        report_form = UserReportForm(request.POST, request.FILES)
    else:
        report_form = UserReportForm()

    context = {
        "profile_user": profile_user,
        "is_following": is_following,
        "can_view_details": can_view_details,
        "posts": posts,
        "posts_count": posts_count,
        "followers_count": followers_count,
        "following_count": following_count,
        "report_form": report_form,
        "is_blocked_by_me": is_blocked_by_me,
        "blocked_between": blocked_between,
    }

    return render(request, 'profile.html', context)


@login_required
@require_POST
def block_user_view(request, username):
    target = get_object_or_404(UserModel, username=username)
    if target.id != request.user.id:
        Block.objects.get_or_create(blocker=request.user, blocked=target)
    return redirect('profile', username=target.username)


@login_required
@require_POST
def unblock_user_view(request, username):
    target = get_object_or_404(UserModel, username=username)
    if target.id != request.user.id:
        Block.objects.filter(blocker=request.user, blocked=target).delete()
    return redirect('profile', username=target.username)