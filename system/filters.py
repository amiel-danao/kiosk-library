import django_filters
from kiosk_library.managers import ReservationManager
from system.models import Book, BookInstance, Reservations
from django.db.models import Q
from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.db import models


class BookFilter(django_filters.FilterSet):
    isbn = django_filters.CharFilter(lookup_expr='icontains')
    publish_date = django_filters.DateFilter(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Book
        fields = ['author', 'isbn', 'genre', 'classification', 'publish_date']


class BookInstanceFilter(django_filters.FilterSet):
    location = django_filters.CharFilter(lookup_expr='icontains')
    search = django_filters.CharFilter(method='filter_search')
    book__isbn = django_filters.CharFilter(lookup_expr='exact')
    book__author = django_filters.CharFilter(label='Author', method='filter_author')
    book__publish_date = django_filters.DateFilter(widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        super(BookInstanceFilter, self).__init__(*args, **kwargs)
        genre = self.filters['book__genre'].label = 'Genre (Hold Ctrl+Left click to select multiple)'

    def filter_search(self, queryset, name, value):
        return queryset.filter(book__title__icontains=value)

    def filter_author(self, queryset, name, value):
        return queryset.filter(Q(book__author__first_name__icontains=value) | Q(book__author__last_name__icontains=value))

    class Meta:
        model = BookInstance
        fields = ['book__author', 'book__isbn', 'book__genre', 'book__classification', "book__publish_date", 'location', 'status']


class OutgoingTransactionFilter(django_filters.FilterSet):
    pass

class ReservationFilter(django_filters.FilterSet):
    date_reserved_gte = django_filters.IsoDateTimeFilter(field_name="date_reserved", lookup_expr='gte')
    class Meta:
        model = Reservations
        fields = ['date_reserved_gte', ]
    # class Meta:
    #     model = Reservations
    #     fields = {
    #         'date_reserved': ('lte', 'gte')
    #     }

    # filter_overrides = {
    #     models.DateTimeField: {
    #         'filter_class': django_filters.IsoDateTimeFilter
    #     },
    # }


