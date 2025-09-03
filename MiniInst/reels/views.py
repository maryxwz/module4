from django import forms
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404

from .forms import ReelsForms
from .models.reels import Reels


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
def all_reels(request):
    reels = Reels.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'all_reels.html', {'reels': reels})


@login_required
def delete_reels(request, pk):
    reels = get_object_or_404(Reels, pk=pk)
    if request.method == 'POST':
        reels.delete()
        return redirect('all_reels')
