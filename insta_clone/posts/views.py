from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import PostForm
from .models import Hashtag, Mention

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()


            for word in post.description.split():
                if word.startswith('#'):
                    tag, created = Hashtag.objects.get_or_create(name=word[1:])
                    post.hashtags.add(tag)
                elif word.startswith('@'):
                    try:
                        mentioned_user = User.objects.get(username=word[1:])
                        Mention.objects.create(post=post, mentioned_user=mentioned_user)
                    except User.DoesNotExist:
                        pass

            return redirect('profile') #тут бєк на профиль ес че, вставите потом
    else:
        form = PostForm()
    return render(request, 'create_post.html', {'form': form})
