import django_filters
from system.models import Book


class BookFilter(django_filters.FilterSet):
    isbn = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Book
        fields = ['author', 'isbn', 'genre', 'classification', 'publish_date']
