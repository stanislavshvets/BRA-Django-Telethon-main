from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views_oauth2
from .views import MyLoginView, RegisterView, ProfileView

app_name = 'Auth'
urlpatterns = [
    path('', MyLoginView.as_view(), name='login'),
    path('sign-out', views_oauth2.sign_out, name='sign_out'),
    path('auth-receiver', views_oauth2.auth_receiver, name='auth_receiver'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('register', RegisterView.as_view(), name='register'),
    path('profile', ProfileView.as_view(), name='profile')
]