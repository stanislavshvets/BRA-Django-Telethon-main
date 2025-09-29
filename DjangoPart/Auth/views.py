from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render
from django.views import View
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy, reverse
from django.contrib.auth import login

from django.apps import apps

from .forms import CustomLoginForm, CustomRegisterForm
from CustomerStats.exchange_rates import get_usd_to_uah_rate, calculate_totals
from CustomerStats.filtrations import filter_orders


def get_client_model():
    # Use the app label (as defined by AppConfig.label, commonly the package name)
    return apps.get_model('CustomerStats', 'Client')


# Create your views here.
class MyLoginView(LoginView):
    template_name = 'CustomerStatsTW/components/authForms/login.html'
    authentication_form = CustomLoginForm
    def get_success_url(self):
        # Redirect to the user's profile after successful sign-in
        return reverse('Auth:profile')


class RegisterView(CreateView):
    template_name = 'CustomerStatsTW/components/authForms/registration.html'
    form_class = CustomRegisterForm   # ось тут замість UserCreationForm
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, form.instance)
        get_client_model().objects.get_or_create(
            user=form.instance,
            defaults={'name': form.instance.username}
        )
        return response

    def get_success_url(self):
        return reverse('Auth:profile')

class ProfileView(View):
    template_name = "CustomerStatsTW/components/userPage/profile.html"

    def get(self, request):
        user = request.user
        client = None
        if user.is_authenticated:
            client = get_client_model().objects.filter(user=user).first()

        usd_to_uah = get_usd_to_uah_rate()
        totals = calculate_totals(client.order_set.all(), usd_to_uah)

        orders, form, query, has_filters = filter_orders(request, client.order_set.all())

        context = {
            'greeting': "Вітаємо,",
            'user': user,
            'client': client,
            'form': form,
            'usd_to_uah': usd_to_uah,
            'has_filters': has_filters,
            **totals,
        }

        return render(request, self.template_name, context)