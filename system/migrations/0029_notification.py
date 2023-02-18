# Generated by Django 4.1.3 on 2023-02-18 17:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0028_reservations_expiry_date_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(blank=True, default='', max_length=256)),
                ('viewed', models.BooleanField(default=False)),
                ('reservation', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='system.reservations')),
            ],
        ),
    ]
