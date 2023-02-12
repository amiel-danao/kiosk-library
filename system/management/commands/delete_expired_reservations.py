from django.core.management.base import BaseCommand
from django.db.models.functions import Now

from system.models import Reservations

class Command(BaseCommand):
    help = 'Remove expired reservations'

    def handle(self, *args, **options):
        Reservations._base_manager.filter(expiry_date__lte=Now()).delete()