from  django.utils import timezone

from django.core.management import BaseCommand

from .models.story import Story


class Command(BaseCommand):
    help = 'Архівує історії, які старші за 24 години'

    def handle(self, *args, **kwargs):
        expired = Story.objects.filter(
            expires_at__lt=timezone.now(),
            is_archived=False
        )
        count = expired.update(is_archived=True)
        self.stdout.write(f'Архівовано {count} історій.')