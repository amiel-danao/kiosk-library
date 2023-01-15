import django_filters
from system.models import Book, BookInstance
from django.db.models import Q
from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class BookFilter(django_filters.FilterSet):
    isbn = django_filters.CharFilter(lookup_expr='icontains')
    publish_date = django_filters.DateFilter(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Book
        fields = ['author', 'isbn', 'genre', 'classification', 'publish_date']


class BookInstanceFilter(django_filters.FilterSet):
    location = django_filters.CharFilter(lookup_expr='icontains')
    book__isbn = django_filters.CharFilter(lookup_expr='exact')
    book__author = django_filters.CharFilter(label='Author', method='filter_author')
    book__publish_date = django_filters.DateFilter(widget=forms.DateInput(attrs={'type': 'date'}))

    def filter_author(self, queryset, name, value):
        return queryset.filter(Q(book__author__first_name__icontains=value) | Q(book__author__last_name__icontains=value))

    class Meta:
        model = BookInstance
        fields = ['book__author', 'book__isbn', 'book__genre', 'book__classification', "book__publish_date", 'location', 'status']


class OutgoingTransactionFilter(django_filters.FilterSet):
    pass