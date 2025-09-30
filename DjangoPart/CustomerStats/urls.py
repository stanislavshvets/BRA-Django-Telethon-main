from django.urls import path
from django.views.generic import DetailView

from . import views

app_name = 'stats'

urlpatterns = [
    path("", views.index, name="index"),
    path('id/<int:client_id>/', views.user_stats, name='stats'),
    path("orders/<int:pk>/delete/", views.delete_order, name="order-delete"),
    path('about/', views.About.as_view(), name='about')
]