from django.db import models


class Post(models.Model):
    author = models.ForeignKey(
        to="users.CustomUser",
        on_delete=models.CASCADE,
        related_name='author',
    )
    image = models.ImageField(upload_to='posts/')
    caption = models.TextField(blank=True)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username} — {self.created_at.strftime('%Y-%m-%d %H:%M')}"
