from django.urls import path, re_path, include
from system.forms import LoginForm
from system import views
from django.contrib.auth import views as auth_views
from rest_framework import routers

app_name = 'system'

router = routers.DefaultRouter()
router.register(r'student', views.StudentViewSet)
router.register(r'book_instance', views.BookInstanceViewSet)
router.register(r'reservation', views.ReservationViewSet)
router.register(r'notification', views.NotificationViewSet)

urlpatterns = [
    path('api/', include((router.urls, 'app_name'), namespace='instance_name')),
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
    path('outgoingtransaction/create_borrow/', views.create_borrow, name='create_borrow'),
    path('admin/sms/', views.sms_view, name='sms'),
    re_path(
        r'^student-autocomplete/$',
        views.StudentAutocomplete.as_view(),
        name='student-autocomplete',
    ),
    path('admin/send_sms/', views.send_sms, name='send_sms'),
    path('api-token-auth/', views.CustomAuthToken.as_view()),
    # path('api/', include((router.urls, 'app_name'), namespace='instance_name')),
]
