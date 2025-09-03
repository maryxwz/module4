from django.db import models

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

    def __str__(self):
        return f"{self.author.username} | {self.created_at}"
