# Generated by Django 4.1.3 on 2023-02-18 17:32

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0029_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
