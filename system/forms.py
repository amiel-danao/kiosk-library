from django import forms
from system.models import BookInstance, OutgoingTransaction

class BookInstanceForm(forms.ModelForm):
    class Meta:
        model = BookInstance
        fields = '__all__'
        exclude = ()

class OutgoingTransactionForm(forms.ModelForm):
    class Meta:
        model = OutgoingTransaction
        fields = '__all__'
        exclude = ()

class IncomingTransactionForm(forms.ModelForm):
    class Meta:
        model = OutgoingTransaction
        fields = '__all__'
        exclude = ()