from django.core.management.base import BaseCommand, CommandError
from proxy.models import ActivatedItem

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        ActivatedItem.objects.create(name='item-1', price=3000)
        items = ActivatedItem.objects.all()
        items.delete()
        print('hello')
