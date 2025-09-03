from django.shortcuts import render, get_object_or_404, redirect
from .models import Post
from .forms import PostForm

def post_list(request):
    posts = Post.objects.filter(is_archived=False).order_by("-created_at")
    return render(request, "posts/post_list.html", {"posts": posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk, is_archived=False)
    return render(request, "posts/post_detail.html", {"post": post})

def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.author = request.user
            form.save()
            return redirect("post_list")
    else:
        form = PostForm()
    return render(request, "posts/post_form.html", {"form": form})

def post_update(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect("post_detail", pk=pk)
    else:
        form = PostForm(instance=post)
    return render(request, "posts/post_form.html", {"form": form})

def post_archive(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    post.is_archived = True
    post.save()
    return redirect("post_list")
