# Generated by Django 4.1.3 on 2023-04-12 05:45

from django.db import migrations, models
import isbn_field.fields
import isbn_field.validators


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0030_notification_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='isbn',
            field=isbn_field.fields.ISBNField(blank=True, default='', max_length=28, validators=[isbn_field.validators.ISBNValidator], verbose_name='ISBN'),
        ),
        migrations.AlterField(
            model_name='bookinstance',
            name='status',
            field=models.IntegerField(choices=[(0, 'On loan'), (1, 'Available'), (2, 'Reserved')], default=1),
        ),
    ]
