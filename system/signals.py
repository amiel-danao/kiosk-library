from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from twilio.rest import Client
import twilio
from kiosk_library.settings import TWILLIO_ACCOUNT_SID, TWILLIO_AUTH_TOKEN, TWILLIO_VIRTUAL_NO
from system.models import BookStatus, IncomingTransaction, Notification, OutgoingTransaction, Reservations


@receiver(post_save, sender=Reservations)
def create_notification(sender, instance, created, **kwargs):
    if created:
        message = f'{instance.student.school_id}, wants to reserve the book: {instance.book_instance.book.title}'
        instance.book_instance.status = BookStatus.RESERVED
        instance.book_instance.save()
        Notification.objects.create(reservation=instance, message=message)

@receiver(post_save, sender=OutgoingTransaction)
def delete_reservation(sender, instance, created, **kwargs):
    if created:

        reservation = Reservations.objects.filter(student=instance.borrower, book_instance=instance.book).first()
        if reservation is not None:            
            reservation.delete()

@receiver(post_delete,sender=Reservations)
def delete_profile(sender,instance,*args,**kwargs):
    instance.book_instance.status = BookStatus.AVAILABLE
    instance.book_instance.save()


@receiver(post_save, sender=OutgoingTransaction)
def new_outgoingtransaction(sender, instance, created, **kwargs):
    if created:
        try:
            client = Client(TWILLIO_ACCOUNT_SID, TWILLIO_AUTH_TOKEN)
            sms_message = f"Good day, we are informing you that you borrowed the book: \"{instance.book.book.title}\" successfully, the return date is: {instance.return_date}  \n Thank you."
            mobile_no = f'+63{instance.borrower.mobile_no[1:]}'
            message = client.messages.create(
                from_=TWILLIO_VIRTUAL_NO,
                to=mobile_no,
                body=sms_message
            )
        except twilio.base.exceptions.TwilioRestException:
            pass

@receiver(post_save, sender=IncomingTransaction)
def new_outgoingtransaction(sender, instance, created, **kwargs):
    if created:
        try:
            client = Client(TWILLIO_ACCOUNT_SID, TWILLIO_AUTH_TOKEN)
            sms_message = f"Good day, thank you for returning the book your borrowed: \"{instance.book.book.title}\""
            mobile_no = f'+63{instance.borrower.mobile_no[1:]}'
            message = client.messages.create(
                from_=TWILLIO_VIRTUAL_NO,
                to=mobile_no,
                body=sms_message
            )
        except twilio.base.exceptions.TwilioRestException:
            pass