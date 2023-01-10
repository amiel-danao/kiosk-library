from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from kiosk_library.managers import CustomUserManager
import uuid
from datetime import date
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from isbn_field import ISBNField
from bookborrowing.models import CatalogueMixin, TimeStampedMixin


class Genre(CatalogueMixin):
    """
    Model representing a book genre.
    """
    class Meta:
        verbose_name = _('genre')
        verbose_name_plural = _('genres')


class Author(TimeStampedMixin):
    """
    Model representing an author.
    """
    first_name = models.CharField(max_length=100)

    last_name = models.CharField(max_length=100)

    date_of_birth = models.DateField('Birth', null=True, blank=True)

    date_of_death = models.DateField('Died', null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = _('author')
        verbose_name_plural = _('authors')

    def __str__(self):
        """
        String for representing the Model object
        """
        return '{0} ({1})'.format(self.first_name, self.last_name)


class Book(CatalogueMixin):
    """
    Model representing a book (but not a specific copy of a book).
    """
    author = models.ManyToManyField(
        Author,
        related_name='books',
        related_query_name='book',
    )

    summary = models.TextField(max_length=1000)

    isbn = ISBNField(unique=True)

    title = models.CharField(max_length=255, default='', blank=False)

    # ManyToManyField used because genre can contain many books.
    # Books can cover many genres.
    # Genre class has already been defined so we can specify the object above.
    genre = models.ManyToManyField(
        Genre,
        related_name='books',
        related_query_name='book'
    )

    publish_date = models.DateField(null=True, blank=True)
    classification = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(999)])

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('book')
        verbose_name_plural = _('books')

    class JSONAPIMeta:
        resource_name = 'books'


class BookInstance(models.Model):
    """
    Model representing a specific copy of a book
    (i.e. that can be borrowed from the library).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='books',
        related_query_name='book'
    )

    LOAN_STATUS = (
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(
        max_length=1, choices=LOAN_STATUS, blank=True, default='a'
    )

    borrow_count = models.PositiveIntegerField(default=0)


    class Meta:
        verbose_name = _('book instance')
        verbose_name_plural = _('book instances')

    def __str__(self):
        """
        String for representing the Model object
        """
        return '{0} ({1})'.format(self.id, self.book.title)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(_("email address"), unique=True)
    picture = models.ImageField(
        upload_to='images/', blank=True, null=True, default='')
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    @property
    def username(self):
        return self.email

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "User"


class Student(models.Model):
    school_id = models.CharField(unique=True, max_length=15, blank=False)

    def __str__(self):
        return self.school_id


class Transaction(models.Model):
    book = models.ForeignKey(BookInstance, on_delete=models.CASCADE,)
    date = models.DateField(auto_now=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE,)
    class Meta:
        abstract = True


class IncomingTransaction(Transaction):
    pass
    

class OutgoingTransaction(Transaction):
    pass