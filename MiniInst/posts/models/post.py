from django.db import models


class Post(models.Model):
    author = models.ForeignKey(
        to="users.CustomUser",
        on_delete=models.CASCADE,
        related_name='posts',
    )
    title = models.CharField(max_length=255, default="Без названия")
    image = models.ImageField(upload_to='posts/')
    caption = models.TextField(blank=True)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} — {self.author.username}"

