from django.urls import path

from . import views

app_name = 'system'

urlpatterns = [
    path('', views.BookInstanceListView.as_view(), name='index'),
    path('qr/<str:pk>/', views.show_qr, name="show-qr"),
]
