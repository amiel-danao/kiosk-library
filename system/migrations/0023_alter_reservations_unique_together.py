# Generated by Django 4.1.3 on 2023-02-12 07:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0022_reservations'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='reservations',
            unique_together={('student', 'book_instance')},
        ),
    ]
