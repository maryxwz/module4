from django.contrib.contenttypes.models import ContentType
from django.db import models

from posts.models import Like

from comments.models.comment import Comment


class Reels(models.Model):
    author = models.ForeignKey(
        to="users.CustomUser",
        on_delete=models.CASCADE,
        related_name='reels',
    )
    content = models.FileField(upload_to="reels/", verbose_name="Video")
    bio = models.TextField(blank=True, null=True, verbose_name="Bio")
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def likes_count(self):
        content_type = ContentType.objects.get_for_model(self)
        return Like.objects.filter(content_type=content_type, object_id=self.id).count()

    @property
    def comments_count(self):
        content_type = ContentType.objects.get_for_model(self)
        return Comment.objects.filter(content_type=content_type, object_id=self.id).count()

    def __str__(self):
        return f"{self.author.username} | {self.created_at}"
