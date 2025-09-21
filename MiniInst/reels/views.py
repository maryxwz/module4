from django import forms
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from .forms import ReelsForms
from .models.reels import Reels
from comments.models.comment import Comment
from posts.models import Like

from .utils import serialize_comment, get_reel_comments


@receiver(post_delete, sender=Reels)
def delete_file_with_reels(sender, instance, **kwargs):
    if instance.content:
        instance.content.delete(False)


@login_required
def create_reels(request):
    if request.method == 'POST':
        form = ReelsForms(request.POST, request.FILES)
        if form.is_valid():
            reels = form.save(commit=False)
            reels.author = request.user
            reels.save()
            return redirect('all_reels')
        else:
            return render(request, 'add_mini_reels.html', {'form': form})
    return render(request, 'add_mini_reels.html', {'form': ReelsForms()})


@login_required
def all_reels_by_user(request):
    reels = Reels.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'all_reels_by_user.html', {'reels': reels})


@login_required
def delete_reels(request, pk):
    reels = get_object_or_404(Reels, pk=pk)
    if request.method == 'POST':
        reels.delete()
        return redirect('all_reels')


@login_required
def all_reels(request):
    reels = Reels.objects.order_by('-created_at').select_related("author")
    return render(request, 'all_reels.html', {'reels': reels})


@login_required
def inf_about_reel(request, pk):
    reel = get_object_or_404(Reels, pk=pk)
    content_type = ContentType.objects.get_for_model(reel)

    comments = Comment.objects.filter(
        content_type=content_type,
        object_id=reel.id,
        is_deleted=False
    ).select_related("author")

    likes_count = Like.objects.filter(
        content_type=content_type,
        object_id=reel.id
    ).count()

    user_liked = Like.objects.filter(
        content_type=content_type,
        object_id=reel.id,
        user=request.user
    ).exists()

    data = {
        "id": reel.id,
        "author": reel.author.username,
        "content": reel.content.url if reel.content else "",
        "likes_count": likes_count,
        "user_liked": user_liked,
        "comments": [
            {
                "author": c.author.username,
                "text": c.text,
                "created_at": c.created_at.strftime("%d.%m.%Y %H:%M"),
            }
            for c in comments
        ],
    }
    return JsonResponse(data)


@login_required
def add_comment(request, pk):
    if request.method == "POST":
        reel = get_object_or_404(Reels, pk=pk)
        content_type = ContentType.objects.get_for_model(reel)
        text = request.POST.get('text')

        if text:
            comment_obj = Comment.objects.create(
                author=request.user,
                text=text,
                content_type=content_type,
                object_id=reel.id
            )

            comments = Comment.objects.filter(
                content_type=content_type,
                object_id=reel.id,
                is_deleted=False
            )

            return JsonResponse({
                'success': True,
                'comment': {
                    "author": comment_obj.author.username,
                    "text": comment_obj.text,
                    "created_at": comment_obj.created_at.strftime("%d.%m.%Y %H:%M"),
                },
                "comment_count": comments.count(),
            })
    return JsonResponse({'success': False}, status=400)


@login_required
def add_like(request, pk):
    if request.method == "POST":
        reel = get_object_or_404(Reels, pk=pk)
        content_type = ContentType.objects.get_for_model(reel)

        like, created = Like.objects.get_or_create(
            content_type=content_type,
            object_id=reel.id,
            user=request.user
        )
        if not created:
            like.delete()
            liked = False
        else:
            liked = True

        like_count = Like.objects.filter(
            content_type=content_type,
            object_id=reel.id
        ).count()

        return JsonResponse({
            'success': True,
            'like_count': like_count,
            "liked": liked,
        })
    return JsonResponse({'success': False}, status=400)


@login_required
def all_reels_comments(request, pk):
    reel = get_object_or_404(Reels, pk=pk)
    content_type = ContentType.objects.get_for_model(reel)

    comments = Comment.objects.filter(
        content_type=content_type,
        object_id=reel.id,
        is_deleted=False
    ).select_related("author")

    return JsonResponse({
        "success": True,
        "comments": [
            {
                "author": c.author.username,
                "text": c.text,
                "created_at": c.created_at.strftime("%d.%m.%Y %H:%M"),
            }
            for c in comments
        ],
    })