from datetime import timezone, datetime

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError, PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from .forms import StoriesForms, ReelsForms
from .models.story import Story, Reels


@login_required
def add_story(request):
    if request.method == 'POST':
        form = StoriesForms(request.POST, request.FILES)
        if form.is_valid():
            story = form.save(commit=False)
            story.author = request.user
            story.save()
            return redirect('all_stories')
    else:
        form = StoriesForms()
    return render(request, 'create_story.html', {'form': form})


@login_required
def all_stories(request):
    now = datetime.now()
    Story.objects.filter(
        author=request.user,
        is_archived=False,
        expires_at__lt=now
    ).update(is_archived=True)

    active_stories = Story.objects.filter(author=request.user, is_archived=False).order_by('-created_at')
    archived_stories = Story.objects.filter(author=request.user, is_archived=True).order_by('-created_at')
    return render(request,
                  'all_stories.html',
                  {'active_stories': active_stories,
                   'archived_stories': archived_stories})


@login_required
def delete_story(request, int_pk):
    story = get_object_or_404(Story, pk=int_pk)

    if story.author != request.user or story.is_archived:
        raise PermissionDenied("You can't delete this story, you are not author or story is archived.")

    if request.method == 'POST':
        story.delete()
        return redirect('all_stories')

    return render(request, 'delete_story.html', {'story': story})


@login_required
def add_mini_reels(request):
    if request.method == 'POST':
        form = ReelsForms(request.POST, request.FILES)
        if form.is_valid():
            reels = form.save(commit=False)
            reels.author = request.user
            reels.save()
            return redirect('all_reels')
    return render(request, 'add_mini_reels.html', {'form': ReelsForms()})


@login_required
def all_reels(request):
    reels = Reels.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'all_reels.html', {'reels': reels})


@login_required
def delete_reels(request, pk):
    reels = get_object_or_404(Reels, pk=pk)
    if request.method == 'POST':
        reels.delete()
        return redirect('all_reels')
    return render(request, 'delete_reels.html', {'reels': reels})
