# Generated by Django 4.1.3 on 2023-07-03 04:11

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0036_alter_outgoingtransaction_incoming_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='incomingtransaction',
            name='due_date',
            field=models.DateField(blank=True, default=django.utils.timezone.now),
        ),
    ]
