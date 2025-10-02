from django.core.management.base import BaseCommand
from stories import scheduler


class Command(BaseCommand):
    help = 'Керування планувальником архівації сторіс'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['start', 'stop', 'restart', 'status', 'run_now'],
            help='Дія для виконання'
        )

    def handle(self, *args, **options):
        action = options['action']

        if action == 'start':
            scheduler.start_scheduler()
            self.stdout.write(
                self.style.SUCCESS('Планувальник запущений')
            )

        elif action == 'stop':
            scheduler.stop_scheduler()
            self.stdout.write(
                self.style.SUCCESS('Планувальник зупинений')
            )

        elif action == 'restart':
            scheduler.stop_scheduler()
            scheduler.start_scheduler()
            self.stdout.write(
                self.style.SUCCESS('Планувальник перезапущений')
            )

        elif action == 'status':
            status = scheduler.get_scheduler_status()
            self.stdout.write(f'Статус планувальника: {status}')

        elif action == 'run_now':
            scheduler.archive_expired_stories()
            self.stdout.write(
                self.style.SUCCESS('Архівацію запущено вручну')
            )