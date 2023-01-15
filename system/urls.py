from django.urls import path
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
    path('outgoingtransaction/create/', views.create_outgoing, name='outgoing_create'),
    path('incomingtransaction/create/', views.create_incoming, name='incoming_create'),
]
