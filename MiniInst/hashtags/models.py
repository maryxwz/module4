from django.db import models


class Hashtag(models.Model):
    hashtag_name = models.CharField(max_length=50)

    def clean(self):
        if not self.hashtag_name.startswith('#'):
            raise ValueError("Хештег має починатися з '#'")