from django.contrib import admin
from django.apps import apps
from django.contrib.auth.models import Group
from system.filters import BookFilter
from system.forms import BookInstanceForm, IncomingTransactionForm, OutgoingTransactionForm
from system.models import SMS, Book, BookInstance, BookStatus, BookType, CustomUser, Genre, IncomingTransaction, Notification, OutgoingTransaction, Author, Reservations, Student, ThesisBook
from django.contrib.admin.views.main import ChangeList
from django.urls import reverse
from django.utils.html import format_html
from rest_framework.authtoken.models import TokenProxy

admin.site.unregister((Group, TokenProxy))
exempted_models = (Group, SMS)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name')

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
    search_fields = ('book__title', 'book__author__first_name', 'book__author__last_name', 'book__isbn',)

    def borrower(self, obj):
        if obj.status == BookStatus.ON_LOAN:
            latest_outgoing = OutgoingTransaction.objects.filter(book=obj).first()
            if latest_outgoing:
                return latest_outgoing.borrower
        return '-'

    def return_date(self, obj):
        if obj.status == BookStatus.ON_LOAN:
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
    fields = ('isbn', 'title', 'genre', 'author', 'classification', 'publish_date', 'thumbnail', 'type')
    list_display = ('isbn', 'title','genres', 'authors',
                    'classification', 'publish_date')
    list_filter = ('isbn',
                   'classification', 'publish_date')
    search_fields = ('isbn', 'title',
                     'classification', 'publish_date')
    filter_horizontal = ("genre", "author")
    
    list_display_links = ('title',)

    def get_queryset(self, request):
        return self.model.objects.filter(type=BookType.BOOK)

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

@admin.register(ThesisBook)
class ThesisMaterialAdmin(BookAdmin):
    def get_queryset(self, request):
        return self.model.objects.filter(type=BookType.THESIS_MATERIALS)

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass

@admin.register(Reservations)
class ReservationAdmin(admin.ModelAdmin):
    readonly_fields = ('student', 'book_instance', 'expiry_date')
    list_display = ('student', 'book_instance', 'date_reserved',)
    
    def has_add_permission(self, request):
        return False
    
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    readonly_fields = ('reservation', 'message', 'date')
    fields = ('reservation', 'message', 'date')
    list_display = ('reservation', 'message', 'date',)

    def change_view(request, object_id, form_url='', extra_context=None):
        return super().change_view(request, object_id, form_url, extra_context)
    
    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        notification = Notification.objects.get(id=object_id)
        notification.viewed = True
        notification.save()
        return super(NotificationAdmin, self).change_view(request, object_id, form_url=form_url, extra_context=extra_context)
    
    def has_add_permission(self, request):
        return False


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
