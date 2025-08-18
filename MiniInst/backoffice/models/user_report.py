from django.db import models


class UserReport(models.Model):
    author = models.ForeignKey(
        to="users.CustomUser",
        on_delete=models.CASCADE,
        related_name='user_reports',
    )
    description = models.TextField(null=False, blank=False)
    content = models.FileField(upload_to="user_reports/", null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.author.username} | {self.created_at.strftime('%Y-%m-%d %H:%M')}"