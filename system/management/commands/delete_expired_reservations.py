from django.core.management.base import BaseCommand
from django.db.models.functions import Now

from system.models import BookInstance, BookStatus, Reservations

class Command(BaseCommand):
    help = 'Remove expired reservations'

    def handle(self, *args, **options):
        qs = Reservations._base_manager.filter(expiry_date__lte=Now())
        
        ids = qs.values_list('book_instance__pk', flat=True)

        BookInstance.objects.filter(id__in=ids).update(status=BookStatus.AVAILABLE)

        qs.delete()
        