from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import StoriesForms
from .models.story import Story





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
    active_stories = Story.objects.filter(author=request.user, is_archived=False).order_by('-created_at')
    archived_stories = Story.objects.filter(author=request.user, is_archived=True).order_by('-created_at')
    return render(request,
                  'all_stories.html',
                  {'active_stories': active_stories,
                   'archived_stories': archived_stories})
