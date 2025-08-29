from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views

from .forms import CustomUserCreationForm
from .models.follow import Follow
from .models.custom_user import CustomUser


class CustomLoginView(auth_views.LoginView):
    def get_success_url(self):
        return reverse_lazy("profile", args=[self.request.user.username]) # щоб після логіну кидало на профіль цього юзера

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
    current_user = request.user

    # Перевірка чи поточний користувач підписаний на профіль
    is_following = Follow.objects.filter(
        follower=current_user,
        following=profile_user
    ).exists()

    can_view_details = (
            current_user == profile_user or
            not profile_user.is_private or
            is_following
    )

    posts = []
    posts_count = 0
    if can_view_details:
        posts = profile_user.posts.all()
        posts_count = posts.count()

    followers_count = profile_user.followers.count() if can_view_details else 0
    following_count = profile_user.following.count() if can_view_details else 0

    context = {
        'profile_user': profile_user,
        'is_following': is_following,
        'can_view_details': can_view_details,
        'posts': posts,
        'posts_count': posts_count,
        'followers_count': followers_count,
        'following_count': following_count,
    }

    return render(request, 'profile.html', context)