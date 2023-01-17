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
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django_tables2 import SingleTableView
from django_filters.views import FilterView
from kiosk_library.managers import CustomUserManager
from system.admin import OutgoingTransactionAdmin
from system.forms import IncomingTransactionForm, LoginForm, OutgoingTransactionForm, RegisterForm, StudentProfileForm
from system.models import Book, BookInstance, CustomUser, IncomingTransaction, OutgoingTransaction, Student
from django_tables2.config import RequestConfig
from system.filters import BookInstanceFilter, OutgoingTransactionFilter
from system.tables import BookInstanceTable, OutgoingTransactionTable
import qrcode
from django.core import serializers
from django.shortcuts import render, redirect
from io import BytesIO
import base64
from django.contrib import messages #import messages
from django.core.mail import send_mail


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


class OutgoingCreateView(CreateView):
    model = OutgoingTransaction
    form_class = OutgoingTransactionForm
    template_name = 'admin/change_form.html'
    success_url = reverse_lazy('admin:system_outgoingtransaction_changelist')


    def form_valid(self, form):
        self.object = form.save(False)
        # make change at the object

        return HttpResponseRedirect(self.get_success_url())

def create_outgoing(request):
    if request.method == 'POST':
        form = OutgoingTransactionForm(request.POST)
        try:
            if form.is_valid():
                # create a new `Band` and save it to the db
                outgoing = form.save()

                outgoing.book.status = 'o'
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

            if incoming.book.status == 'a':
                messages.error(request, f'This book {incoming.book.book.title} was already returned!')
                return HttpResponseRedirect(reverse_lazy('admin:system_incomingtransaction_changelist'))
            incoming.book.status = 'a'
            

            id = request.POST.get('book', None)
            outgoing = OutgoingTransaction.objects.filter(book__id=id).latest('date_borrowed')
            incoming.borrower = outgoing.borrower

            incoming.book.save()
            incoming.save()

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
                                    last_name=request.POST.get('last_name', ''))
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


class StudentProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    form_class = StudentProfileForm
    template_name = 'system/profile.html'
    success_url = reverse_lazy('system:student_profile', )

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully.')
        return super().form_valid(form)


    def get_success_url(self):
        return reverse('system:student_profile', kwargs={'pk': self.object.id})


class StudentBorrowedListView(LoginRequiredMixin, SingleTableView, FilterView):
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

    # def get_context_data(self, **kwargs):
    #     context = super(StudentBorrowedListView, self).get_context_data(**kwargs)
    #     species=self.get_queryset()
    #     f = self.filterset_class(self.request.GET, queryset=species)
    #     context['filter'] = f
    #     table = self.table_class(f.qs)
    #     RequestConfig(self.request).configure(table)
    #     context['table'] = table

        return context