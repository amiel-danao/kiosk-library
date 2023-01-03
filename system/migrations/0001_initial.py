# Generated by Django 4.1.3 on 2023-01-03 15:45

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import isbn_field.fields
import isbn_field.validators
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True, verbose_name='created date')),
                ('last_modified', models.DateTimeField(auto_now=True, null=True, verbose_name='last modified')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('date_of_birth', models.DateField(blank=True, null=True, verbose_name='Birth')),
                ('date_of_death', models.DateField(blank=True, null=True, verbose_name='Died')),
            ],
            options={
                'verbose_name': 'author',
                'verbose_name_plural': 'authors',
                'ordering': ['last_name', 'first_name'],
            },
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True, verbose_name='created date')),
                ('last_modified', models.DateTimeField(auto_now=True, null=True, verbose_name='last modified')),
                ('name', models.CharField(max_length=600, verbose_name='name')),
                ('is_active', models.BooleanField(default=True, verbose_name='is active')),
                ('was_deleted', models.BooleanField(default=False, verbose_name='was deleted')),
                ('summary', models.TextField(max_length=1000)),
                ('isbn', isbn_field.fields.ISBNField(max_length=28, unique=True, validators=[isbn_field.validators.ISBNValidator], verbose_name='ISBN')),
                ('title', models.CharField(default='', max_length=255)),
                ('publish_date', models.DateField(blank=True, null=True)),
                ('classification', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(999)])),
                ('author', models.ManyToManyField(related_name='books', related_query_name='book', to='system.author')),
            ],
            options={
                'verbose_name': 'book',
                'verbose_name_plural': 'books',
            },
        ),
        migrations.CreateModel(
            name='BookInstance',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('status', models.CharField(blank=True, choices=[('o', 'On loan'), ('a', 'Available'), ('r', 'Reserved')], default='a', max_length=1)),
                ('borrow_count', models.PositiveIntegerField(default=0)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='books', related_query_name='book', to='system.book')),
            ],
            options={
                'verbose_name': 'book instance',
                'verbose_name_plural': 'book instances',
            },
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True, verbose_name='created date')),
                ('last_modified', models.DateTimeField(auto_now=True, null=True, verbose_name='last modified')),
                ('name', models.CharField(max_length=600, verbose_name='name')),
                ('is_active', models.BooleanField(default=True, verbose_name='is active')),
                ('was_deleted', models.BooleanField(default=False, verbose_name='was deleted')),
            ],
            options={
                'verbose_name': 'genre',
                'verbose_name_plural': 'genres',
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now=True)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='system.bookinstance')),
            ],
        ),
        migrations.AddField(
            model_name='book',
            name='genre',
            field=models.ManyToManyField(related_name='books', related_query_name='book', to='system.genre'),
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('picture', models.ImageField(blank=True, default='', null=True, upload_to='images/')),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'User',
            },
        ),
    ]
