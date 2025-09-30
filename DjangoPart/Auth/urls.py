from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import MyLoginView, RegisterView, ProfileView

app_name = 'Auth'
urlpatterns = [
    path('', MyLoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('register', RegisterView.as_view(), name='register'),
    path('profile', ProfileView.as_view(), name='profile')
]