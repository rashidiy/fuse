from django.core.management.base import BaseCommand
from django.utils.timezone import now


class Command(BaseCommand):
    help = 'Displays current time'

    def handle(self, *args, **kwargs):
        time = now().strftime('%X')
        self.stdout.write("It's now %s" % time)