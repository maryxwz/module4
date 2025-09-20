import json
from django.http.response import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_POST
from django.contrib import messages
from types import SimpleNamespace

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
        return reverse_lazy("users:profile", args=[self.request.user.username])


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
        return redirect('users:register')
    return render(request, 'home.html', {'profile_user': profile_user, 'posts': all_posts, 'stories': all_stories})


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('users:profile', username=request.user.username)
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

    report_form = UserReportForm(request.POST or None, request.FILES or None)

    incoming_requests_count = 0
    outgoing_requests_count = 0
    if current_user == profile_user:
        incoming_requests_count = FollowRequest.objects.filter(
            to_user=current_user, status=FollowRequest.PENDING
        ).count()
        outgoing_requests_count = FollowRequest.objects.filter(
            from_user=current_user, status=FollowRequest.PENDING
        ).count()

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
        "incoming_requests_count": incoming_requests_count,
        "outgoing_requests_count": outgoing_requests_count,
    }
    return render(request, 'profile.html', ctx)


@login_required
@require_POST
def block_user_view(request, username):
    target = get_object_or_404(UserModel, username=username)
    if target.id != request.user.id:
        Block.objects.get_or_create(blocker=request.user, blocked=target)
    return redirect('users:profile', username=target.username)


@login_required
@require_POST
def unblock_user_view(request, username):
    target = get_object_or_404(UserModel, username=username)
    if target.id != request.user.id:
        Block.objects.filter(blocker=request.user, blocked=target).delete()
    return redirect('users:profile', username=target.username)


@login_required
@require_POST
def follow_user_view(request, username):
    target = get_object_or_404(UserModel, username=username)
    me = request.user
    if target == me:
        return redirect('users:profile', username=target.username)

    # нельзя подписываться, если кто-то заблокировал
    if Block.objects.filter(blocker=me, blocked=target).exists() or Block.objects.filter(blocker=target, blocked=me).exists():
        return redirect('users:profile', username=target.username)

    toast_text = None
    if bool(getattr(target, "is_private", False)):
        # всегда приводим заявку к PENDING
        FollowRequest.objects.update_or_create(
            from_user=me,
            to_user=target,
            defaults={"status": FollowRequest.PENDING},
        )
        toast_text = "Запит на підписку надіслано"
    else:
        Follow.objects.get_or_create(follower=me, following=target)
        toast_text = f"Ви підписалися на @{target.username}"

    if request.headers.get("HX-Request") == "true":
        resp = _follow_button_partial(request, target)
        followers = target.followers.count()
        following = target.following.count()
        resp["HX-Trigger"] = json.dumps({
            "profile_counts": {
                "username": target.username,
                "followers_count": followers,
                "following_count": following
            },
            "toast": {"type": "success", "text": toast_text}
        })
        return resp

    messages.success(request, toast_text)
    return redirect('users:profile', username=target.username)


@login_required
@require_POST
def unfollow_user_view(request, username):
    target = get_object_or_404(UserModel, username=username)
    me = request.user
    if target == me:
        return redirect('users:profile', username=target.username)

    Follow.objects.filter(follower=me, following=target).delete()
    FollowRequest.objects.filter(from_user=me, to_user=target, status=FollowRequest.PENDING).delete()

    if request.headers.get("HX-Request") == "true":
        resp = _follow_button_partial(request, target)
        followers = target.followers.count()
        following = target.following.count()
        resp["HX-Trigger"] = json.dumps({
            "profile_counts": {
                "username": target.username,
                "followers_count": followers,
                "following_count": following
            },
            "toast": {"type": "info", "text": f"Ви відписалися від @{target.username}"}
        })
        return resp

    messages.info(request, f"Ви відписалися від @{target.username}")
    return redirect('users:profile', username=target.username)


@login_required
@require_POST
def follow_request_accept_view(request, pk):
    fr = get_object_or_404(FollowRequest, pk=pk, to_user=request.user)
    fr.status = FollowRequest.APPROVED
    fr.save(update_fields=["status"])
    Follow.objects.get_or_create(follower=fr.from_user, following=fr.to_user)

    entries = list(FollowRequest.objects.select_related('from_user').filter(
        to_user=request.user, status=FollowRequest.PENDING
    ))
    if request.headers.get("HX-Request") == "true" or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        resp = render(request, "users/_requests_incoming.html", {"entries": entries})
        followers = request.user.followers.count()
        following = request.user.following.count()
        resp["HX-Trigger"] = json.dumps({
            "profile_counts": {
                "username": request.user.username,
                "followers_count": followers,
                "following_count": following
            },
            "toast": {"type": "success", "text": f"Ви схвалили запит від @{fr.from_user.username}"}
        })
        return resp

    messages.success(request, f"Ви схвалили запит від @{fr.from_user.username}")
    return redirect('users:profile', username=request.user.username)


@login_required
@require_POST
def follow_request_reject_view(request, pk):
    fr = get_object_or_404(FollowRequest, pk=pk, to_user=request.user)
    fr.status = FollowRequest.REJECTED
    fr.save(update_fields=["status"])

    entries = list(FollowRequest.objects.select_related('from_user').filter(
        to_user=request.user, status=FollowRequest.PENDING
    ))
    if request.headers.get("HX-Request") == "true" or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        resp = render(request, "users/_requests_incoming.html", {"entries": entries})
        followers = request.user.followers.count()
        following = request.user.following.count()
        resp["HX-Trigger"] = json.dumps({
            "profile_counts": {
                "username": request.user.username,
                "followers_count": followers,
                "following_count": following
            },
            "toast": {"type": "info", "text": f"Ви відхилили запит від @{fr.from_user.username}"}
        })
        return resp

    messages.info(request, f"Ви відхилили запит від @{fr.from_user.username}")
    return redirect('users:profile', username=request.user.username)


@login_required
def followers_list_view(request, username):
    profile_user = get_object_or_404(CustomUser, username=username)
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
    profile_user = get_object_or_404(CustomUser, username=username)
    rels = Follow.objects.select_related('following').filter(follower=profile_user)
    users = [rel.following for rel in rels]
    is_me = (request.user == profile_user)
    return render(request, "users/_following_list.html", {
        "profile_user": profile_user,
        "users": users,
        "is_me": is_me,
    })


@login_required
def follow_requests_incoming_view(request, username):
    if request.user.username != username:
        raise Http404()
    q = FollowRequest.objects.select_related('from_user').filter(
        to_user=request.user, status=FollowRequest.PENDING
    )
    entries = [fr for fr in q]
    return render(request, "users/_requests_incoming.html", {"entries": entries})


@login_required
def follow_requests_outgoing_view(request, username):
    if request.user.username != username:
        raise Http404()
    q = FollowRequest.objects.select_related('to_user').filter(
        from_user=request.user, status=FollowRequest.PENDING
    )
    entries = [fr for fr in q]
    return render(request, "users/_requests_outgoing.html", {"entries": entries})


@login_required
@require_POST
def follow_request_cancel_view(request, username):
    to_user = get_object_or_404(CustomUser, username=username)
    FollowRequest.objects.filter(
        from_user=request.user, to_user=to_user, status=FollowRequest.PENDING
    ).delete()

    render_kind = request.POST.get("render")
    if request.headers.get("HX-Request") == "true" or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        if render_kind == "button":
            resp = _follow_button_partial(request, to_user)
            followers = to_user.followers.count()
            following = to_user.following.count()
            resp["HX-Trigger"] = json.dumps({
                "profile_counts": {
                    "username": to_user.username,
                    "followers_count": followers,
                    "following_count": following
                },
                "toast": {"type": "info", "text": "Запит скасовано"}
            })
            return resp

        entries = list(FollowRequest.objects.select_related('to_user').filter(
            from_user=request.user, status=FollowRequest.PENDING
        ))
        resp = render(request, "users/_requests_outgoing.html", {"entries": entries})
        resp["HX-Trigger"] = json.dumps({"toast": {"type": "info", "text": "Запит скасовано"}})
        return resp

    messages.info(request, "Запит скасовано")
    return redirect('users:profile', username=request.user.username)


def _follow_button_partial(request, target_user):
    profile_user = target_user
    current_user = request.user
    is_following = Follow.objects.filter(follower=current_user, following=profile_user).exists()
    is_blocked_by_me = Block.objects.filter(blocker=current_user, blocked=profile_user).exists()
    blocked_me = Block.objects.filter(blocker=profile_user, blocked=current_user).exists()
    blocked_between = is_blocked_by_me or blocked_me
    pending_request = FollowRequest.objects.filter(
        from_user=current_user, to_user=profile_user, status=FollowRequest.PENDING
    ).first()
    return render(request, "users/_follow_button.html", {
        "profile_user": profile_user,
        "is_following": is_following,
        "pending_request": pending_request,
        "is_blocked_by_me": is_blocked_by_me,
        "blocked_between": blocked_between,
    })


@login_required
def account_settings_view(request):
    me = request.user
    if request.method == "POST":
        make_private = request.POST.get("is_private") == "on"
        me.is_private = make_private
        me.save(update_fields=["is_private"])
        messages.success(request, "Акаунт зроблено приватним." if make_private else "Акаунт зроблено публічним.")
        return redirect("users:settings")
    form = SimpleNamespace(
        is_private=SimpleNamespace(
            name="is_private",
            id_for_label="id_is_private",
            value=bool(getattr(me, "is_private", False)),
        )
    )
    return render(request, "backoffice/settings.html", {"form": form})