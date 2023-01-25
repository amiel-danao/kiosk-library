from django.urls import path, re_path
from system.forms import LoginForm
from system import views
from django.contrib.auth import views as auth_views

app_name = 'system'

urlpatterns = [
    path('', views.BookInstanceListView.as_view(), name='index'),
    path('qr/<str:pk>/', views.show_qr, name="show-qr"),
    path('accounts/login/',
         auth_views.LoginView.as_view(authentication_form=LoginForm, redirect_authenticated_user=True), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('accounts/register/', views.register_view, name='register'),
    path('accounts/verify/<str:id>/', views.verify_account_view, name='create'),
    path('accounts/send_verification/', views.send_verification, name='send_verification'),
    path('accounts/profile/<int:pk>/', views.StudentProfileUpdateView.as_view(), name='student_profile'),
    path('student/books/<int:pk>/', views.StudentBorrowedListView.as_view(), name='student_borrowed_books'),
    path('outgoingtransaction/create/', views.create_outgoing, name='outgoing_create'),
    path('incomingtransaction/create/', views.create_incoming, name='incoming_create'),
    path('admin/sms/', views.sms_view, name='sms'),
    re_path(
        r'^student-autocomplete/$',
        views.StudentAutocomplete.as_view(),
        name='student-autocomplete',
    ),
    path('admin/send_sms/', views.send_sms, name='send_sms'),
]
