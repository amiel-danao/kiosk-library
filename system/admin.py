from django.contrib import admin
from django.apps import apps
from django.contrib.auth.models import Group
from system.forms import BookInstanceForm, IncomingTransactionForm, OutgoingTransactionForm
from system.models import Book, BookInstance, IncomingTransaction, OutgoingTransaction
from django.contrib.admin.views.main import ChangeList
from django.urls import reverse
from django.utils.html import format_html



admin.site.unregister(Group)
exempted_models = (Group, )


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'qr', )

    def qr(self, obj):
        my_id = str(obj.pk)
        # url = "{% url 'system:show-qr' pk={0} %}".format(my_id)
        url = reverse(
            f'system:show-qr', kwargs={'pk': my_id}
        ) 
        return format_html('<a target="_blank" href="{0}" >{1}<i class="bi bi-qr-code"></i></a>', url, my_id)


@admin.register(OutgoingTransaction)
class OutgoingTransactionAdmin(admin.ModelAdmin):

    def changelist_view(self, request, extra_context=None):
        scan_form = OutgoingTransactionForm()
        
        my_context = {
            'scan': {
                'modal_title': 'Outgoing Book <i class="bi bi-book"></i>',
                'modal_accept_text': 'Accept Outgoing <i class="bi bi-check-circle-fill"></i>',
            },
            'scan_form': scan_form
        }
        return super(OutgoingTransactionAdmin, self).changelist_view(request,
            extra_context=my_context)

@admin.register(IncomingTransaction)
class IncomingTransactionAdmin(admin.ModelAdmin):

    def changelist_view(self, request, extra_context=None):
        scan_form = IncomingTransactionForm()
        
        my_context = {
            'scan': {
                'modal_title': 'Incoming Book <i class="bi bi-book"></i>',
                'modal_accept_text': 'Accept Incoming <i class="bi bi-check-circle-fill"></i>',
            },
            'scan_form': scan_form
        }
        return super(IncomingTransactionAdmin, self).changelist_view(request,
            extra_context=my_context)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    fields = ('isbn', 'title', 'genre', 'author', )
    list_display = ('isbn', 'title','genres', 'authors',
                    'classification_number', 'publish_date')
    list_filter = ('isbn',
                   'classification', 'publish_date')
    search_fields = ('isbn', 'title',
                     'classification', 'publish_date')

    def changelist_view(self, request, extra_context=None):
        my_context = {
        }
        return super(BookAdmin, self).changelist_view(request,
            extra_context=my_context)

    def authors(self, obj):
        return ",".join([str(p) for p in obj.author.all()])

    def genres(self, obj):
        return ",".join([str(p) for p in obj.genre.all()])

    def classification_number(self, obj):
        return str(obj.classification).zfill(3)



app_config = apps.get_app_config('system')
models = app_config.get_models()

for model in models:
    if model.__class__ in exempted_models:
        continue
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass

admin.site.site_header = "Kiosk Book Library"
admin.site.site_title = 'NCST Kiosk Book Library System'
admin.site.index_title = "Welcome to Kiosk Book Library"
