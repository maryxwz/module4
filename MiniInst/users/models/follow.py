from django.db import models


class Follow(models.Model):
    follower = models.ForeignKey(
        to="CustomUser",
        on_delete=models.CASCADE,
        related_name='following',
    )
    following = models.ForeignKey(
        to="CustomUser",
        on_delete=models.CASCADE,
        related_name='followers',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower} → {self.following}"
