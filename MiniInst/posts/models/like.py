from django.db import models


class Like(models.Model):
    user = models.ForeignKey(
        to="users.CustomUser",
        on_delete=models.CASCADE,
        related_name='likes',
    )
    post = models.ForeignKey(
        to="Post",
        on_delete=models.CASCADE,
        related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user.username} ❤️ {self.post.id}"
