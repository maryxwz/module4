import random

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from .models.custom_user import CustomUser
from posts.models.post import Post
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist


class CustomLoginView(auth_views.LoginView):
    def get_success_url(self):
        return reverse_lazy("profile", args=[self.request.user.username]) # щоб після логіну кидало на профіль цього юзера


def home_view(request):
    all_posts = list(Post.objects.all())

    if not all_posts:
        random_post = None
    else:
        random_post = random.choice(all_posts)

    try:
        profile_user = CustomUser.objects.get(username=request.user.username)
    except ObjectDoesNotExist:
        return redirect('register')

    return render(request, 'home.html', {
        'profile_user': profile_user,
        'post': random_post
    })


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile',username=request.user.username)
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(CustomUser, username=username)
    print('Looking for', profile_user) # перевірка чи підтягнувся юзернейм
    if request.user.username != profile_user.username or profile_user.is_private == True:
        raise PermissionDenied("Цей профіль закритий") # ось тут замінити на редірект до сторінки (таск в трело)
    return render(request, 'profile.html', {'user': profile_user})
