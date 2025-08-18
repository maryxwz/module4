from django.db import models
import uuid

class Direct(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user1 = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='directs_as_user1')
    user2 = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='directs_as_user2')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user1} - {self.user2}"

    def get_receiver(self, current_user):
        if current_user == self.user1:
            return self.user2
        elif current_user == self.user2:
            return self.user1
        return None
        
    def save(self, *args, **kwargs):
        if self.user1.id > self.user2.id:
            self.user1, self.user2 = self.user2, self.user1
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user1', 'user2'], name='unique_direct_between_users')
        ]
