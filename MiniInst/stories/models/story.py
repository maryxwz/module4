from datetime import timedelta
from django.db import models
from django.utils import timezone

def story_expiration():
    return timezone.now() + timedelta(hours=24)


class Story(models.Model):
    author = models.ForeignKey(
        to="users.CustomUser",
        on_delete=models.CASCADE,
        related_name='stories',
    )

    content = models.FileField(upload_to="stories/")
    is_archived = models.BooleanField(default=False)
    expires_at = models.DateTimeField(default=story_expiration)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_active(self):
        return timezone.now() < self.expires_at

    def __str__(self):
        return f"{self.author.username} | {self.created_at.strftime('%Y-%m-%d %H:%M')}"

