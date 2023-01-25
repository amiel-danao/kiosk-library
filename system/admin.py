from django.contrib import admin
from django.apps import apps
from django.contrib.auth.models import Group
from system.filters import BookFilter
from system.forms import BookInstanceForm, IncomingTransactionForm, OutgoingTransactionForm
from system.models import SMS, Book, BookInstance, CustomUser, IncomingTransaction, OutgoingTransaction, Author, Student
from django.contrib.admin.views.main import ChangeList
from django.urls import reverse
from django.utils.html import format_html
from django.utils import timezone


admin.site.unregister(Group)
exempted_models = (Group, SMS)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name')

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    readonly_fields = ('email', 'date_joined', 'last_login')
    fields = ('email', 'is_staff', 'is_active', 'date_joined', 'last_login')
    list_display = ('email', 'is_staff', 'is_active', 'date_joined', 'last_login')

@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'borrow_count')
    fields = ('book', 'status', "borrow_count", 'location')
    list_display = ('book', 'status', 'borrower', "return_date", 'borrow_count', 'qr', )
    list_filter = ('book__genre', 'book__classification', 'status')
    search_fields = ('book__author', 'book__isbn',)

    def borrower(self, obj):
        if obj.status == 'o':
            latest_outgoing = OutgoingTransaction.objects.filter(book=obj).first()
            if latest_outgoing:
                return latest_outgoing.borrower
        return '-'

    def return_date(self, obj):
        if obj.status == 'o':
            latest_outgoing = OutgoingTransaction.objects.filter(book=obj).first()
            if latest_outgoing:
                return latest_outgoing.return_date
        return '-'

    def qr(self, obj):
        my_id = str(obj.pk)
        url = reverse(
            f'system:show-qr', kwargs={'pk': my_id}
        ) 
        return format_html('<a target="_blank" href="{0}" >{1}<i class="bi bi-qr-code"></i></a>', url, my_id)

    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)
    #     return qs

    # def changelist_view(self, request, extra_context=None):
    #     queryset = self.get_queryset(request)
    #     filter = BookInstanceAdminFilter(request.GET, queryset=queryset)
    #     my_context = {
    #         'filter' : filter
    #     }
    #     return super(BookInstanceAdmin, self).changelist_view(request,
    #         extra_context=my_context)

@admin.register(OutgoingTransaction)
class OutgoingTransactionAdmin(admin.ModelAdmin):

    readonly_fields = ('borrower', 'book', 'date_borrowed')
    fields = ('book', 'borrower', 'date_borrowed', 'return_date')
    list_display = ('book', 'borrower', 'date_borrowed', 'return_date')

    def has_add_permission(self, request):
        return False

    def changelist_view(self, request, extra_context=None):
        scan_form = OutgoingTransactionForm()
        
        my_context = {
            'scan': {
                'modal_title': 'Outgoing Book <i class="bi bi-book"></i>',
                'modal_accept_text': 'Accept Outgoing <i class="bi bi-check-circle-fill"></i>',
                'url': reverse('system:outgoing_create')
            },
            'scan_out_form': scan_form
        }
        return super(OutgoingTransactionAdmin, self).changelist_view(request,
            extra_context=my_context)

@admin.register(IncomingTransaction)
class IncomingTransactionAdmin(admin.ModelAdmin):

    readonly_fields = ('borrower', 'book', 'date_returned')
    fields = ('book', 'borrower', 'date_returned')
    list_display = ('book', 'borrower', 'date_returned')

    def has_add_permission(self, request):
        return False

    def changelist_view(self, request, extra_context=None):
        scan_form = IncomingTransactionForm()
        
        my_context = {
            'scan': {
                'modal_title': 'Incoming Book <i class="bi bi-book"></i>',
                'modal_accept_text': 'Accept Incoming <i class="bi bi-check-circle-fill"></i>',
                'url': reverse('system:incoming_create')
            },
            'scan_in_form': scan_form
        }
        return super(IncomingTransactionAdmin, self).changelist_view(request,
            extra_context=my_context)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    readonly_fields = ('email', )
    list_display = ('email', 'school_id', 'first_name', 'last_name')

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    fields = ('isbn', 'title', 'genre', 'author', 'classification', 'publish_date')
    list_display = ('isbn', 'title','genres', 'authors',
                    'classification', 'publish_date')
    list_filter = ('isbn',
                   'classification', 'publish_date')
    search_fields = ('isbn', 'title',
                     'classification', 'publish_date')
    filter_horizontal = ("genre", "author")

    def changelist_view(self, request, extra_context=None):
        queryset = self.get_queryset(request)
        filter = BookFilter(request.GET, queryset=queryset)
        my_context = {
            'filter' : filter
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

# for model in models:
#     if model.__class__ in exempted_models:
#         continue
#     try:
#         admin.site.register(model)
#     except admin.sites.AlreadyRegistered:
#         pass

admin.site.site_header = "Kiosk Book Library"
admin.site.site_title = 'NCST Kiosk Book Library System'
admin.site.index_title = "Welcome to Kiosk Book Library"
