from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from system.models import Notification, Reservations


@receiver(post_save, sender=Reservations)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        message = f'{instance.student.school_id}, wants to reserve the book: {instance.book_instance.book.title}'
        Notification.objects.create(reservation=instance, message=message)