from django.db import models


class Comment(models.Model):
    author = models.ForeignKey(
        to="users.CustomUser",
        on_delete=models.CASCADE,
        related_name='comments',
    )
    post = models.ForeignKey(
        to="posts.Post",
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(null=False, blank=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author.username} — {self.text}"
