import django_filters
from system.models import Book, BookInstance


class BookFilter(django_filters.FilterSet):
    isbn = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Book
        fields = ['author', 'isbn', 'genre', 'classification', 'publish_date']


class BookInstanceFilter(django_filters.FilterSet):
    book__isbn = django_filters.CharFilter(lookup_expr='exact')

    class Meta:
        model = BookInstance
        fields = ['book__author', 'book__isbn', 'book__genre', 'book__classification', 'status']