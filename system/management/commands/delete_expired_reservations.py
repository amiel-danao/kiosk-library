from django.core.management.base import BaseCommand
from django.db.models.functions import Now
from django.utils import timezone
from datetime import datetime, timedelta
from system.models import BookInstance, BookStatus, Reservations

class Command(BaseCommand):
    help = 'Remove expired reservations'

    def handle(self, *args, **options):
        d = datetime.now() - timedelta(hours=1)
        all = Reservations._base_manager.first()
        qs = Reservations._base_manager.filter(expiry_date__lt=d)
        
        ids = qs.values_list('book_instance__pk', flat=True)

        BookInstance.objects.filter(id__in=ids).update(status=BookStatus.AVAILABLE)

        qs.delete()
        