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

def generate_school_id():
    
    try_student_id = get_next_school_id()
    while(Student.objects.filter(school_id=try_student_id).first() is not None):
        try_student_id = get_next_school_id()
    return try_student_id

def get_next_school_id():
    year = timezone.now().year
    latest_student = Student.objects.order_by('-pk')[0]
    current_index = 0
    if latest_student is not None:
        current_index = int(latest_student.school_id.split('-')[1])
    current_index += 1

    return f'{year}-{str(current_index).zfill(5)}'

class Student(models.Model):
    school_id = models.CharField(max_length=10, blank=False, unique=True, default=generate_school_id)
    email = models.EmailField(unique=True, blank=False, default='')
    first_name = models.CharField(blank=False, default='', max_length=50)
    middle_name = models.CharField(blank=True, max_length=50)
    last_name = models.CharField(blank=True, max_length=50)
    mobile_no = models.CharField(blank=True, max_length=11)

    def __str__(self):
        return self.school_id

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
    )

    status = models.CharField(
        max_length=1, choices=LOAN_STATUS, blank=True, default='a'
    )

    borrow_count = models.PositiveIntegerField(default=0)

    location = models.CharField(max_length=200, blank=True)


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
    is_active = models.BooleanField(default=False)
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


class Transaction(models.Model):
    book = models.ForeignKey(BookInstance, on_delete=models.CASCADE,)
    borrower = models.ForeignKey(Student, on_delete=models.CASCADE,)
    class Meta:
        abstract = True


class IncomingTransaction(Transaction):
    date_returned = models.DateField(default=timezone.now, blank=True)
    
    def __str__(self) -> str:
        return f'{self.book.book.title} - {self.borrower}'
    

class OutgoingTransaction(Transaction):
    date_borrowed = models.DateField(default=timezone.now, blank=True)
    return_date = models.DateField(null=True)

    def __str__(self) -> str:
        return f'{self.book.book.title} - {self.borrower}'

class SMS(models.Model):
    students = models.ManyToManyField(Student)
    message = models.CharField(max_length=150, blank=False)