from django.http import HttpResponse
from django_tables2 import SingleTableView
from django_filters.views import FilterView
from system.models import BookInstance
from django_tables2.config import RequestConfig
from system.filters import BookInstanceFilter
from system.tables import BookInstanceTable
import qrcode
from django.core import serializers
from django.shortcuts import render
from io import BytesIO
import base64

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def show_qr(request, pk):
    instance = BookInstance.objects.get(pk=pk)
    data = serializers.serialize('json', [ instance, ])
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    # qr.save(f"{pk}.png")
    return HttpResponse(f'<img src=data:image/png;base64,{img_str}>')



class BookInstanceListView(SingleTableView, FilterView):
    model = BookInstance
    table_class = BookInstanceTable
    template_name = 'system/index.html'
    filterset_class = BookInstanceFilter
    table_pagination = {
        'per_page': 5,
    }
    strict=False

    def get_queryset(self):
        qs = super().get_queryset()
        return qs

    def get_context_data(self, **kwargs):
        context = super(BookInstanceListView, self).get_context_data(**kwargs)
        species=self.get_queryset()
        f = self.filterset_class(self.request.GET, queryset=species)
        context['filter'] = f
        table = self.table_class(f.qs)
        RequestConfig(self.request).configure(table)
        context['table'] = table

        return context