from django.db import models
import uuid

class DirectMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    direct = models.ForeignKey('direct.Direct', on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='sent_direct_messages')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}: {self.message[:20]}"
