import django_tables2 as tables
from system.models import BookInstance, OutgoingTransaction
from django.utils.translation import gettext_lazy as _


class BookInstanceTable(tables.Table):
    class Meta:
        model = BookInstance
        template_name = "django_tables2/bootstrap5.html"
        fields = ("book", "book__author", "book__genre", "book__publish_date", "status", 'location', "borrow_count")
        empty_text = _("No books found for this search query.")
        attrs = {'class': 'table table-hover shadow records-table'}
        # row_attrs = {'data-href': lambda book: book.get_absolute_url}


class OutgoingTransactionTable(tables.Table):
    # status = tables.Column(empty_values=())

    class Meta:
        model = OutgoingTransaction
        template_name = "django_tables2/bootstrap5.html"
        fields = ("book__book__title", "date_borrowed", "return_date")
        empty_text = _("No books borrowed.")
        attrs = {'class': 'table table-hover shadow records-table'}

    # def render_status(self, value, record):
    #     if record:
    #         book = record.book
    #         if book.status == 'o':
    #             return 'On hand'
    #     return 'Returned'