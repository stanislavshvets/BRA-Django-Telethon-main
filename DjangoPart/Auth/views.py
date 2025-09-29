from asgiref.sync import sync_to_async
from django.contrib.auth.views import LoginView, LogoutView
from django.core.files.uploadedfile import UploadedFile
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy, reverse
from django.contrib.auth import login

from django.apps import apps

from .forms import CustomLoginForm, CustomRegisterForm, UploadFileForm
from CustomerStats.exchange_rates import get_usd_to_uah_rate, calculate_totals
from CustomerStats.filtrations import filter_orders

from MyDjangoBot.settings import BASE_DIR


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

    async def get_context_data(self, request, upload_file_form=None):
        """Хелпер для формування контексту (щоб не дублювати код)."""
        user = request.user

        client = None
        if user.is_authenticated:
            client = await sync_to_async(
                lambda: get_client_model().objects.filter(user=user).first()
            )()

        usd_to_uah = get_usd_to_uah_rate()

        # orders = client.order_set.all() → через sync_to_async
        orders = []
        if client:
            orders = await sync_to_async(lambda: client.order_set.all())()

        totals = await calculate_totals(orders, usd_to_uah)

        orders, form, query, has_filters = filter_orders(request, orders)

        context = {
            "greeting": "Вітаємо,",
            "is_user_authenticated": user.is_authenticated,
            "user": user,
            "client": client,
            "uploadFileForm": upload_file_form or UploadFileForm(),
            "form": form,
            "usd_to_uah": usd_to_uah,
            "has_filters": has_filters,
            **totals,
        }
        return context

    async def get(self, request):
        context = await self.get_context_data(request)
        return await sync_to_async(
            lambda: render(request, self.template_name, context)
        )()

    async def post(self, request):
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data["title"]
            file = form.cleaned_data["file"]

            save_dir = BASE_DIR.parent / "common_data" / "models"
            await sync_to_async(save_dir.mkdir)(parents=True, exist_ok=True)

            file_path = save_dir / file.name

            # асинхронне збереження файлу
            async with await sync_to_async(open)(file_path, "wb+") as destination:
                for chunk in file.chunks():
                    await sync_to_async(destination.write)(chunk)

            return redirect("profile")

        # якщо форма не валідна — формуємо контекст з помилками
        context = await self.get_context_data(request, upload_file_form=form)
        return await sync_to_async(
            lambda: render(request, self.template_name, context)
        )()