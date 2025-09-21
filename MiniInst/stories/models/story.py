from datetime import timedelta
from django.db import models
from django.utils import timezone


def story_expiration():
    return timezone.now() + timedelta(hours=24)


class StoryManager(models.Manager):
    def active(self):
        return self.filter(
            is_archived=False,
            expires_at__gt=timezone.now()
        )

    def archived(self):
        return self.filter(is_archived=True)

    def archive_expired(self):
        return self.filter(
            expires_at__lt=timezone.now(),
            is_archived=False
        ).update(is_archived=True)


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

    objects = StoryManager()

    def is_active(self):
        return timezone.now() < self.expires_at and not self.is_archived

    def archive_if_expired(self):
        if not self.is_active() and not self.is_archived:
            self.is_archived = True
            self.save()
            return True
        return False

    def __str__(self):
        return f"{self.author.username} | {self.created_at.strftime('%Y-%m-%d %H:%M')}"

