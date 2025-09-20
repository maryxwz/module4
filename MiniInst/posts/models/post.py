from django.db import models
from django.db.models import Q
from django.conf import settings


class PostQuerySet(models.QuerySet):
    def visible_to(self, user):
        if getattr(user, "is_anonymous", True):
            return self
        return self.exclude(
            Q(author__blocks_received__blocker=user) |
            Q(author__blocks_initiated__blocked=user)
        )

class Post(models.Model):
    author = models.ForeignKey(to="users.CustomUser", on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=255, default="Без названия")
    image = models.ImageField(upload_to="posts/")
    caption = models.TextField(blank=True)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = PostQuerySet.as_manager()

    @property
    def repost_count(self):
        return self.reposted_by.count()

    def __str__(self):
        return f"{self.author.username} — {self.title}"

class SavedPost(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_posts"
    )
    post = models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        related_name="saved_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")

    def __str__(self):
        return f"{self.user.username} saved {self.post.id}"

class Repost(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reposts"
    )
    post = models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        related_name="reposted_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")

    def __str__(self):
        return f"{self.user.username} reposted {self.post.id}"