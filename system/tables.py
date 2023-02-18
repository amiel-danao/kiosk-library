import django_tables2 as tables
from system.models import BookInstance, OutgoingTransaction
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django_tables2 import TemplateColumn

class BookInstanceTable(tables.Table):
    borrow = TemplateColumn(template_code=f'<a type="button" href="#" class="btn btn-primary">Borrow</a>')

    class Meta:
        model = BookInstance
        template_name = "django_tables2/bootstrap5.html"
        fields = ("book", "book__author", "book__genre", "book__publish_date", "status", 'location', "borrow_count")
        empty_text = _("No books found for this search query.")
        attrs = {'class': 'table table-hover shadow records-table'}


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