from django.core.management.base import BaseCommand
from django.db.models.functions import Now
from django.utils import timezone
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from twilio.rest import Client
import twilio
import pytz
from kiosk_library.settings import TWILLIO_ACCOUNT_SID, TWILLIO_AUTH_TOKEN, TWILLIO_VIRTUAL_NO
from system.models import BookInstance, BookStatus, OutgoingTransaction, Reservations, Student

class Command(BaseCommand):
    help = 'Sms auto send, day of borrowing, day before returning, day returned'

    #this function will only handle the day before returning
    def handle(self, *args, **options):
        tz = pytz.timezone('Asia/Manila')

        client = Client(TWILLIO_ACCOUNT_SID, TWILLIO_AUTH_TOKEN)
        today = datetime.today()

        qs = OutgoingTransaction._base_manager.filter(return_date__gte=today)

        for transaction in qs:
            one_day_before = transaction.return_date - timedelta(days=1)

            if datetime.date(today) >= one_day_before:
                
                try:
                    sms_message = f"Good day, we are informing you that the book: \"{transaction.book.book.title}\" you borrowed should be returned tomorrow  \n Thank you."
                    mobile_no = f'+63{transaction.borrower.mobile_no[1:]}'
                    message = client.messages.create(
                        from_=TWILLIO_VIRTUAL_NO,
                        to=mobile_no,
                        body=sms_message
                    )
                except twilio.base.exceptions.TwilioRestException:
                    pass