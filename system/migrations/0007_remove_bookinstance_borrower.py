# Generated by Django 4.1.3 on 2023-01-15 10:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0006_rename_student_incomingtransaction_borrower_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookinstance',
            name='borrower',
        ),
    ]