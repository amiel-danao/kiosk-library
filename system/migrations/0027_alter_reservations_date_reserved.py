# Generated by Django 4.1.3 on 2023-02-12 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0026_alter_reservations_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservations',
            name='date_reserved',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
    ]
