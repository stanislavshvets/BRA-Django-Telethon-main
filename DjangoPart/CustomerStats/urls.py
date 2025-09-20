from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('id/<int:client_id>/', views.user_stats, name='stats'),
    path("orders/<int:pk>/delete/", views.delete_order, name="order-delete")
]