from datetime import datetime
import django
from django.urls import reverse
import django_tables2 as tables
from pydantic import ValidationError
from system.models import BookInstance, BookStatus, OutgoingTransaction, Reservations, Student
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django_tables2 import TemplateColumn
from django.utils import timezone

class BookInstanceTable(tables.Table):
    borrow = tables.Column(empty_values=())

    class Meta:
        model = BookInstance
        template_name = "django_tables2/bootstrap5.html"
        fields = ("book", "book__author", "book__genre", "book__publish_date", "status", 'location', "borrow_count")
        empty_text = _("No books found for this search query.")
        attrs = {'class': 'table table-hover shadow records-table'}

    def render_status(self, record):
        return BookStatus(record.status).label

    def render_borrow(self, record):
        if not self.request.user.is_authenticated or record.status != BookStatus.AVAILABLE:
            return '-'
        token = django.middleware.csrf.get_token(self.request)
        url = reverse('system:create_borrow')
        student = Student.objects.filter(email=self.request.user.email).first()
        if student is None:
            return '-'
        return_date = timezone.make_aware(datetime.now()).strftime('%Y-%m-%d')
        html_string = f'''
        <form method="post" action="{url}">
            <input name="csrfmiddlewaretoken" value="{token}" hidden>
            <input type="text" id="id_book_title" class="form-control-plaintext" name="book_title" value="{record.book.title}" hidden>            
            <input type="text" id="id_book" name="book" value="{record.pk}" hidden>
            <input type="text" id="id_borrower" name="borrower" value="{student.school_id}" hidden>
            <input type="text" id="id_return_date" name="return_date" value="{return_date}" hidden>
            <button type="submit" href="#" class="btn btn-primary">Borrow</button>
        </form>'''
        return mark_safe(html_string)


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