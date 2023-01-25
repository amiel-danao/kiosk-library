from dal import autocomplete
from django.utils.translation import gettext as _
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from system.context_processors import MOBILE_NO_REGEX
from .models import SMS, CustomUser
from django.core.exceptions import ValidationError
from django import forms
from kiosk_library.managers import CustomUserManager
from system.models import Book, BookInstance, IncomingTransaction, OutgoingTransaction, Student

class BookInstanceForm(forms.ModelForm):
    class Meta:
        model = BookInstance
        fields = '__all__'
        exclude = ()

class OutgoingTransactionForm(forms.ModelForm):

    book = forms.CharField()
    borrower = forms.CharField()

    class Meta:
        model = OutgoingTransaction
        fields = '__all__'
        exclude = ()
        widgets = {
            'return_date': forms.widgets.DateInput(attrs={'type': 'date', 'class': 'restricted_today_date'}), 
        }

    def clean_book(self):
        data = self.cleaned_data['book']

        try:
            book = BookInstance.objects.get(id=data)
            if book.status == 'o':
                raise ValidationError(f'{book.book.title} is currently borrowed!')
            return book
        except Student.DoesNotExist as error:
            raise ValidationError(f'Book with id {data} doesn\'t exist!')

    def clean_borrower(self):
        data = self.cleaned_data['borrower']

        try:
            return Student.objects.get(school_id=data)
        except Student.DoesNotExist as error:
            raise ValidationError(f'Student with id {data} doesn\'t exist!')
        except ValidationError as error:
            raise ValidationError(f'Student with id {data} doesn\'t exist!')

        # Check some condition over data
        # raise ValidationError for bad results
        # else return data

class IncomingTransactionForm(forms.ModelForm):

    # borrower = forms.CharField()

    class Meta:
        model = IncomingTransaction
        fields = '__all__'
        exclude = ('date_returned', 'borrower')

    # def clean_borrower(self):

    #     try:
    #         id = self.cleaned_data['book']
    #         if id is None:
    #             raise ValidationError(f'book with id {id} not found!')
    #         outgoing = OutgoingTransaction.objects.filter(id=id).latest()
    #         return outgoing.borrower
    #     except Student.DoesNotExist as error:
    #         raise ValidationError(f'book with id {id} error!')
    #     except ValidationError as error:
    #         raise ValidationError(f'book with id {id} error!')






class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ("email", "password1", "password2")

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class StudentProfileForm(forms.ModelForm):

    school_id = forms.RegexField(
        required=True,
        regex='^(?:\d{4}-\d{5})$',
        error_messages = {'invalid': _("Please input a valid Student Id No pattern: YYYY-xxxxx")}, label='Student Id No.')

    mobile_no = forms.RegexField(
        required=True,
        regex=MOBILE_NO_REGEX,
        error_messages = {'invalid': _("Please input a valid mobile number")}, label='Mobile No.')

    def __init__(self, *args, **kwargs):
        super(StudentProfileForm, self).__init__(*args, **kwargs)
        self.fields['email'].disabled = True

    class Meta:
        model = Student
        fields = '__all__'
        exclude = ('date_returned', 'borrower')


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email', required=True)

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                _("Please confirm your email so you can log in."),
                code='inactive',
            )

MYCHOICES = ((1,1), (2,2))

class SMSForm(forms.ModelForm):
    # recepients = forms.Field(widget=autocomplete.ListSelect2(url='system:student-autocomplete'))
    message = forms.CharField(widget=forms.Textarea(attrs={"rows":6, "maxlength":150}), required=True)
    recepients = forms.CharField(widget=forms.TextInput(attrs={"hidden":""}), required=False)

    class Meta:
        model = SMS
        exclude = ()
        widgets = {
            'students': autocomplete.ModelSelect2Multiple(url='system:student-autocomplete')
        }