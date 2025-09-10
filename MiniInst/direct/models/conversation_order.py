from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

class ConversationOrder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conversation_orders')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=36)  # використовуємо строкове представлення UUID/int
    position = models.IntegerField()

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')
        ordering = ['position']

    def __str__(self):
        return f"{self.user} — {self.content_type}({self.object_id}) @ {self.position}"
