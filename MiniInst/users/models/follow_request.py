from django.conf import settings
from django.db import models
from django.utils import timezone

class FollowRequest(models.Model):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

    STATUS_CHOICES = [
        (PENDING, "pending"),
        (APPROVED, "approved"),
        (REJECTED, "rejected"),
    ]

    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="sent_follow_requests", on_delete=models.CASCADE)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="received_follow_requests", on_delete=models.CASCADE)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = (("from_user", "to_user"),)

    def __str__(self):
        return f"{self.from_user} -> {self.to_user} [{self.status}]"