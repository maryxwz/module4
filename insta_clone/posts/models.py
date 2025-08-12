from django.db import models
from django.contrib.auth.models import User

class Hashtag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='posts/')
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    hashtags = models.ManyToManyField(Hashtag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username} - {self.description[:20]}"

class Mention(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    mentioned_user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.mentioned_user.username} in post {self.post.id}"
