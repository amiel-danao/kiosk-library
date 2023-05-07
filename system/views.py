from rest_framework import filters
import django_filters.rest_framework
from rest_framework import generics, mixins, viewsets
from django.conf import settings
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client
from django.contrib.auth.signals import user_logged_in
from dal import autocomplete
from django.db.models import Q
from django.contrib import admin
import vonage
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import views as auth_views
from django.shortcuts import render,redirect
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from smtplib import SMTPDataError
from django.contrib.auth import logout as authlogout
from django.contrib.auth.decorators import login_required as login_required
from django.contrib.auth import login
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, Http404
from django_tables2 import SingleTableView
from django_filters.views import FilterView
from kiosk_library.managers import CustomUserManager
from system.admin import OutgoingTransactionAdmin
from system.forms import BookFilterFormHelper, IncomingTransactionForm, LoginForm, OutgoingTransactionForm, RegisterForm, SMSForm, StudentProfileForm
from system.models import Book, BookInstance, BookStatus, BookType, CustomUser, Genre, IncomingTransaction, OutgoingTransaction, Reservations, Student, Notification
from django_tables2.config import RequestConfig
from system.filters import BookInstanceFilter, OutgoingTransactionFilter, ReservationFilter
from system.serializers import BookInstanceSerializer, GenreSerializer, NotificationSerializer, OutgoingTransactionSerializer, ReservationsSerializer, StudentSerializer
from system.tables import BookInstanceTable, OutgoingTransactionTable
import qrcode
from django.core import serializers
from django.shortcuts import render, redirect
from io import BytesIO
import base64
from django.contrib import messages #import messages
from django.core.mail import send_mail
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import viewsets, filters

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def show_qr(request, pk):
    instance = BookInstance.objects.get(pk=pk)
    data = serializers.serialize('json', [ instance, instance.book])
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
        qs = super().get_queryset().filter(book__type=BookType.BOOK).order_by('book__title')
        return qs

    def get_context_data(self, **kwargs):
        context = super(BookInstanceListView, self).get_context_data(**kwargs)
        qs=self.get_queryset().order_by('book__title')
        f = self.filterset_class(self.request.GET, queryset=qs)
        context['filter'] = f
        table = self.table_class(f.qs)
        RequestConfig(self.request).configure(table)
        context['table'] = table

        
        return context

class ThesisBookListView(SingleTableView, FilterView):
    model = BookInstance
    table_class = BookInstanceTable
    template_name = 'system/index.html'
    filterset_class = BookInstanceFilter
    table_pagination = {
        'per_page': 5,
    }
    strict=False

    def get_queryset(self):
        qs = super().get_queryset().filter(book__type=BookType.THESIS_MATERIALS)
        return qs

    def get_context_data(self, **kwargs):
        context = super(ThesisBookListView, self).get_context_data(**kwargs)
        qs=self.get_queryset().order_by('book__title')
        f = self.filterset_class(self.request.GET, queryset=qs)
        context['filter'] = f
        context['thesis_only'] = True
        table = self.table_class(f.qs)
        RequestConfig(self.request).configure(table)
        context['table'] = table

        
        return context

class OutgoingCreateView(CreateView):
    model = OutgoingTransaction
    form_class = OutgoingTransactionForm
    template_name = 'admin/change_form.html'
    success_url = reverse_lazy('admin:system_outgoingtransaction_changelist')


    def form_valid(self, form):
        self.object = form.save(False)
        # make change at the object

        return HttpResponseRedirect(self.get_success_url())

def create_borrow(request):
    if request.method == 'POST':
        form = OutgoingTransactionForm(request.POST)
        try:
            if form.is_valid():
                outgoing = form.save()
                outgoing.book.status = BookStatus.ON_LOAN
                outgoing.book.borrow_count += 1
                outgoing.book.save()

                try:
                    student = Student.objects.get(email=request.user.email)
                    message = f'{student.school_id}, borrowed the book: {outgoing.book.book.title}'
                    Notification.objects.create(reservation=None, message=message)
                except Student.DoesNotExist as _:
                    pass
                messages.success(request, 'Book borrowed successfully!')
                return redirect('system:index')
            else:
                # for field in form.errors:
                #     field_value = request.POST.get(field)
                #     for error in field:
                messages.error(request, form.errors)
                return HttpResponseRedirect(reverse_lazy('system:index'))
        except BookInstance.DoesNotExist as error:
            messages.error(request, error)
            return HttpResponseRedirect(reverse_lazy('system:index'))

def create_outgoing(request):
    if request.method == 'POST':
        form = OutgoingTransactionForm(request.POST)
        try:
            if form.is_valid():
                # create a new `Band` and save it to the db
                outgoing = form.save()

                outgoing.book.status = BookStatus.ON_LOAN
                outgoing.book.borrow_count += 1
                outgoing.book.save()
                # redirect to the detail page of the band we just created
                # we can provide the url pattern arguments as arguments to redirect function
                return redirect('admin:system_outgoingtransaction_change', outgoing.id)
            else:
                # for field in form.errors:
                #     field_value = request.POST.get(field)
                #     for error in field:
                messages.error(request, form.errors)
                return HttpResponseRedirect(reverse_lazy('admin:system_outgoingtransaction_changelist'))
        except BookInstance.DoesNotExist as error:
            messages.error(request, error)
            return HttpResponseRedirect(reverse_lazy('admin:system_outgoingtransaction_changelist'))
    return HttpResponseBadRequest()
    # return HttpResponseRedirect(reverse_lazy('admin:system_outgoingtransaction_changelist'))

def create_incoming(request):
    if request.method == 'POST':
        form = IncomingTransactionForm(request.POST)
        if form.is_valid():
            # create a new `Band` and save it to the db
            incoming = form.save(commit=False)

            if incoming.book.status == BookStatus.AVAILABLE:
                messages.error(request, f'This book {incoming.book.book.title} was already returned!')
                return HttpResponseRedirect(reverse_lazy('admin:system_incomingtransaction_changelist'))
            incoming.book.status = BookStatus.AVAILABLE            
            incoming.book.save()

            try:
                id = request.POST.get('book', None)
                outgoing = OutgoingTransaction.objects.filter(book__id=id).latest('date_borrowed')
                incoming.borrower = outgoing.borrower
                incoming.save()
            except OutgoingTransaction.DoesNotExist as exception:
                messages.error(request, f'This book {incoming.book.book.title} has no outgoing transaction!')
                return HttpResponseRedirect(reverse_lazy('admin:system_incomingtransaction_changelist'))
            
            # IncomingTransaction.objects.create(book=incoming.book, borrower=outgoing.borrower)
            # redirect to the detail page of the band we just created
            # we can provide the url pattern arguments as arguments to redirect function
            return redirect('admin:system_incomingtransaction_change', incoming.id)
        else:
            # for field in form.errors:
            #     field_value = request.POST.get(field)
            #     for error in field:
            messages.error(request, form.errors)
            return HttpResponseRedirect(reverse_lazy('admin:system_incomingtransaction_changelist'))
    return HttpResponseBadRequest()

def verify_account_view(request, id):
    if request.method == "GET":
        account = CustomUser.objects.get(id=id)
        account.is_active = True
        account.save()
        return render(request=request, template_name='registration/verified.html')
    return HttpResponseBadRequest()


def send_verification(request):
    if request.method == "POST":
        email = request.POST.get('email', None)
        if email is not None:
            try:
                user = CustomUser.objects.get(email=email)
                if user.is_active:
                    messages.error(request, f'User with email {email} is already registered')
                    return redirect('system:login')
            except CustomUser.DoesNotExist:
                messages.error(request, f'User with email {email} is not yet registered')
                return redirect('system:register')
            try:
                domain = request.get_host()
                link = reverse('system:create', kwargs={'id':user.id})
                send_verification_email(request.POST.get('email'), f'{domain}{link}')
                messages.success(request, f'An email verification was sent to {email}.')
                return redirect('system:register')
            except SMTPDataError as error:
                messages.error(request, f'{error}\n Please try again later.')
                return redirect('system:index')

    return HttpResponseBadRequest()

class CustomLoginView(auth_views.LoginView): # 1. <--- note: this is a class-based view

    form_class = LoginForm # 2. <--- note: define form here?

    def get_success_url(self):
        url = self.get_redirect_url()
        return url or reverse_lazy('system:index')

def send_verification_email(email, link):
    
    send_mail(
        'NCST Kiosk - Student Account Registration',
        f'To verify your account, please follow this link: {link} \n Please disregard this email if you do not create this account!',
        'ncst.kiosk.gmail.com',
        (email, ),
        fail_silently=False,
    )


def register_view(request):
    form = RegisterForm()
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = False
            user.save()
            Student.objects.create(email=user.email, 
                                    first_name=request.POST.get('first_name', ''),
                                    middle_name=request.POST.get('middle_name', ''),
                                    last_name=request.POST.get('last_name', ''),
                                    mobile_no=request.POST.get('mobile_no'))
            # login(request, user)
            try:
                domain = request.get_host()
                link = reverse('system:create', kwargs={'id':user.id})
                send_verification_email(request.POST.get('email'), f'{domain}{link}')
                messages.success(request, "Registration successful. Please check your email to verify your account.")
                return redirect('system:index')
            except SMTPDataError as error:
                messages.error(request, f'{error}\n Please try again later.')
                return redirect('system:index')
            
        messages.error(
            request, "Unsuccessful registration. Invalid information.")
    return render(request=request, template_name="registration/register.html", context={"form": form})

@login_required
def logout_view(request):
    authlogout(request)

    return redirect('system:login')

class StudentsOnlyView(object):

    def has_permissions(self):
        if self.request.user.is_superuser:
            return False
        return True

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permissions():
            raise Http404('You do not have permission.')
        return super(StudentsOnlyView, self).dispatch(
            request, *args, **kwargs)


class StudentProfileUpdateView(LoginRequiredMixin, StudentsOnlyView, UpdateView):
    model = Student
    form_class = StudentProfileForm
    template_name = 'system/profile.html'
    success_url = reverse_lazy('system:student_profile', )

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully.')
        return super().form_valid(form)


    def get_success_url(self):
        return reverse('system:student_profile', kwargs={'pk': self.object.id})


class StudentBorrowedListView(LoginRequiredMixin, StudentsOnlyView, SingleTableView, FilterView):
    model = OutgoingTransaction
    table_class = OutgoingTransactionTable
    template_name = 'system/student_borrowed_books.html'
    filterset_class = OutgoingTransactionFilter
    table_pagination = {
        'per_page': 5,
    }
    strict=False

    def render_to_response(self, context):
        if self.request.user.is_superuser:
            return redirect('system:index')

        
        return super().render_to_response(context)

    def get_queryset(self):
        
        qs = super().get_queryset()
        qs = qs.filter(borrower__email=self.request.user.email)
        return qs


def sms_view(request):
    context = {}

    context['form'] = SMSForm()


    return render(request, 'admin/sms_notification.html', context)


def send_sms(request):
    context = {}
    if request.method == "POST":
        context['form'] = SMSForm(request.POST)
        # client = vonage.Client(key="282f39f9", secret="wCG7JXwLDPlVW9Rm")
        # sms = vonage.Sms(client)

        message = request.POST.get('message', 'No message')
        
        id_string = request.POST.get('recepients', '')

        ids = id_string.split(',')
        recepients = Student.objects.filter(school_id__in=ids)

        client = Client(settings.TWILLIO_ACCOUNT_SID, settings.TWILLIO_AUTH_TOKEN)

        for recepient in recepients:
            mobile_no = recepient.mobile_no.lstrip('0')
            if not mobile_no:
                messages.error(request, f'mobile no. of student {recepient.school_id} is invalid')
                continue
            # responseData = sms.send_message(
            #     {
            #         "from": 'Vonage APIs',
            #         "to": f'63{mobile_no}',
            #         "text": f'{admin.site.site_title} \n {message}\n',
            #     }
            # )

            try:
                message = client.messages.create(
                    body=f'\n{admin.site.site_title} \n {message}\n',
                    from_=settings.TWILLIO_VIRTUAL_NO,
                    to=f'+63{mobile_no}'
                )
                messages.success(request, f"Message sent successfully. {mobile_no}")
            except TwilioRestException as responseData:
                messages.error(request, f"Message failed for {mobile_no} with error: {responseData}")
            

            # if responseData["messages"][0]["status"] == "0":
            #     messages.success(request, f"Message sent successfully. {mobile_no}")
            # else:
            #     messages.error(request, f"Message failed for {mobile_no} with error: {responseData['messages'][0]['error-text']}")

        return redirect('system:sms')

    context['form'] = SMSForm()
    return redirect('system:sms')

    


class StudentAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Student.objects.none()

        qs = Student.objects.filter(~Q(mobile_no=''))

        if self.q:
            qs = qs.filter(school_id__istartswith=self.q)

        return qs





def create_non_existing_student_profile(sender, user, request, **kwargs):
    if not user.is_superuser:
        existing_profile = Student.objects.filter(email=user.email).first()
        if existing_profile is None:
            Student.objects.create(email=user.email, 
                                    first_name=user.email.split('@')[0])

user_logged_in.connect(create_non_existing_student_profile)


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data,
                                            context={'request': request})
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
        except Exception as e:
            return HttpResponseBadRequest(content=e)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })
    
class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    filterset_fields = ['email',]
    # filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    # lookup_field = 'email'
    # lookup_url_kwarg = 'email'
    # lookup_value_regex = '[\w@.]+'

class BookInstanceViewSet(viewsets.ModelViewSet):
    queryset = BookInstance.objects.all()
    serializer_class = BookInstanceSerializer
    filterset_fields = ['status']
    # filter_class = BookInstanceFilter
    filter_backends = [filters.SearchFilter, django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['book__title', '=book__isbn', 'book__author__first_name', 'book__author__last_name']
    ordering = ('book__title',)
    # filter_backends = [django_filters.rest_framework.DjangoFilterBackend]

class OutgoingTransactionViewSet(viewsets.ModelViewSet):
    queryset = OutgoingTransaction.objects.all()
    serializer_class = OutgoingTransactionSerializer
    filterset_fields = ['borrower',]
    # filter_class = BookInstanceFilter
    filter_backends = [filters.SearchFilter, django_filters.rest_framework.DjangoFilterBackend]
    # search_fields = ['book__title', '=book__isbn', 'book__author__first_name', 'book__author__last_name']


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservations.objects.all()
    serializer_class = ReservationsSerializer
    filterset_fields = ['student__school_id', 'book_instance']    
    # filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    # lookup_field = 'student'
    # lookup_url_kwarg = 'student'
    # lookup_value_regex = '[\w@.]+'

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    filterset_fields = ['viewed', ]

class GenreList(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Genre.objects.all().distinct().values_list('name', flat=True)
    serializer_class = GenreSerializer

    def list(self, request):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset()
        serializer = GenreSerializer(queryset, many=True)
        return Response(list(queryset))