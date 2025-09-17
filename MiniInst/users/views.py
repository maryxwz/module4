import random

from django.http.response import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.contrib.auth import views as auth_views
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator

from backoffice.forms import UserReportForm
from .forms import CustomUserCreationForm
from .models.follow import Follow
from .models.custom_user import CustomUser
from .models.block import Block
from posts.models.post import Post
from stories.models.story import Story
from .models.follow_request import FollowRequest

UserModel = get_user_model()

class CustomLoginView(auth_views.LoginView):
    def get_success_url(self):
        return reverse_lazy("profile", args=[self.request.user.username])

def home_view(request):
    all_posts = list(Post.objects.all())
    for post in list(all_posts):
        if getattr(post.author, "is_private", False):
            all_posts.remove(post)
    all_stories = list(Story.objects.all())
    for story in list(all_stories):
        if getattr(story.author, "is_private", False):
            all_stories.remove(story)
    if request.user.is_authenticated:
        blocked_ids = set(Block.objects.filter(blocker=request.user).values_list('blocked_id', flat=True))
        blocked_me_ids = set(Block.objects.filter(blocked=request.user).values_list('blocker_id', flat=True))
        banned_user_ids = blocked_ids.union(blocked_me_ids)
        if banned_user_ids:
            all_posts = [p for p in all_posts if p.author_id not in banned_user_ids]
    try:
        profile_user = CustomUser.objects.get(username=request.user.username)
    except ObjectDoesNotExist:
        return redirect('register')
    return render(request, 'home.html', {'profile_user': profile_user, 'posts': all_posts, 'stories': all_stories})

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
    if getattr(profile_user, "is_banned", False):
        raise Http404("Профіль заблокован")

    is_following = Follow.objects.filter(follower=current_user, following=profile_user).exists()
    is_blocked_by_me = Block.objects.filter(blocker=current_user, blocked=profile_user).exists()
    blocked_me = Block.objects.filter(blocker=profile_user, blocked=current_user).exists()
    blocked_between = is_blocked_by_me or blocked_me

    can_view_details = (current_user == profile_user or not profile_user.is_private or is_following)
    can_view_details = can_view_details and not blocked_between

    posts = []
    posts_count = 0
    if can_view_details:
        posts = profile_user.posts.all()
        posts_count = posts.count()

    followers_count = profile_user.followers.count() if can_view_details else 0
    following_count = profile_user.following.count() if can_view_details else 0

    pending_request = None
    if not is_following and current_user != profile_user:
        pending_request = FollowRequest.objects.filter(
            from_user=current_user, to_user=profile_user, status=FollowRequest.PENDING
        ).first()

    if request.method == "POST":
        report_form = UserReportForm(request.POST, request.FILES)
    else:
        report_form = UserReportForm()

    ctx = {
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
        "pending_request": pending_request,
    }
    return render(request, 'profile.html', ctx)

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

@login_required
@require_POST
def follow_user_view(request, username):
    target = get_object_or_404(UserModel, username=username)
    me = request.user
    if target == me:
        return redirect('profile', username=target.username)
    if Block.objects.filter(blocker=me, blocked=target).exists() or Block.objects.filter(blocker=target, blocked=me).exists():
        return redirect('profile', username=target.username)

    if getattr(target, "is_private", False):
        fr, created = FollowRequest.objects.get_or_create(
            from_user=me, to_user=target, defaults={"status": FollowRequest.PENDING}
        )
        if not created and fr.status == FollowRequest.REJECTED:
            fr.status = FollowRequest.PENDING
            fr.save(update_fields=["status"])
    else:
        Follow.objects.get_or_create(follower=me, following=target)

    if request.headers.get("HX-Request") == "true":
        return _follow_partial_response(request, target)
    return redirect('profile', username=target.username)

@login_required
@require_POST
def unfollow_user_view(request, username):
    target = get_object_or_404(UserModel, username=username)
    me = request.user
    if target == me:
        return redirect('profile', username=target.username)
    Follow.objects.filter(follower=me, following=target).delete()
    FollowRequest.objects.filter(from_user=me, to_user=target, status=FollowRequest.PENDING).delete()
    if request.headers.get("HX-Request") == "true":
        return _follow_partial_response(request, target)
    return redirect('profile', username=target.username)

@login_required
@require_POST
def follow_request_accept_view(request, pk):
    fr = get_object_or_404(FollowRequest, pk=pk, to_user=request.user)
    fr.status = FollowRequest.APPROVED
    fr.save(update_fields=["status"])
    Follow.objects.get_or_create(follower=fr.from_user, following=fr.to_user)
    if request.headers.get("HX-Request") == "true":
        return _follow_partial_response(request, fr.from_user)
    return redirect('profile', username=fr.from_user.username)

@login_required
@require_POST
def follow_request_reject_view(request, pk):
    fr = get_object_or_404(FollowRequest, pk=pk, to_user=request.user)
    fr.status = FollowRequest.REJECTED
    fr.save(update_fields=["status"])
    if request.headers.get("HX-Request") == "true":
        return _follow_partial_response(request, fr.from_user)
    return redirect('profile', username=fr.from_user.username)

def _follow_partial_response(request, target_user):
    """
    Возвращаем HTML блока кнопки + oob-апдейты счетчиков.
    ВАЖНО: рендерим тот partial, который у тебя уже существует — users/_follow_list.html
    (у тебя он сейчас содержит кнопки и OOB-апдейты).
    """
    profile_user = target_user
    current_user = request.user
    is_following = Follow.objects.filter(follower=current_user, following=profile_user).exists()
    followers_count = profile_user.followers.count()
    following_count = profile_user.following.count()
    pending_request = FollowRequest.objects.filter(
        from_user=current_user, to_user=profile_user, status=FollowRequest.PENDING
    ).first()
    return render(request, "users/_follow_list.html", {
        "profile_user": profile_user,
        "is_following": is_following,
        "pending_request": pending_request,
        "followers_count": followers_count,
        "following_count": following_count,
    })

# --------- НОВОЕ: списки підписників/підписок для модалки ---------

@login_required
def followers_list_view(request, username):
    """
    Список тех, кто ПОДПИСАЛСЯ на profile_user.
    """
    profile_user = get_object_or_404(CustomUser, username=username)

    # Все фолловеры (люди, у которых follower -> profile_user в поле following)
    rels = Follow.objects.select_related('follower').filter(following=profile_user)
    users = [rel.follower for rel in rels]

    is_me = (request.user == profile_user)
    return render(request, "users/_followers_list.html", {
        "profile_user": profile_user,
        "users": users,
        "is_me": is_me,
    })


@login_required
def following_list_view(request, username):
    """
    Список тех, на КОГО ПОДПИСАН profile_user.
    """
    profile_user = get_object_or_404(CustomUser, username=username)

    # Все, на кого он подписан (у него follower = profile_user)
    rels = Follow.objects.select_related('following').filter(follower=profile_user)
    users = [rel.following for rel in rels]

    is_me = (request.user == profile_user)
    return render(request, "users/_following_list.html", {
        "profile_user": profile_user,
        "users": users,
        "is_me": is_me,
    })