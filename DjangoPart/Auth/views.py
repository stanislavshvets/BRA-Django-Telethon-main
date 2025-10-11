import os
import pathlib

from asgiref.sync import sync_to_async
from django.contrib.auth.views import LoginView, LogoutView
from django.core.files.uploadedfile import UploadedFile
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy, reverse
from django.contrib.auth import login
import aiofiles
from django.apps import apps
from django.utils import timezone
from django.utils.timezone import localtime
from tzlocal import get_localzone

from Utils.Utils import create_model_path, convert_model_path_to_video_path
from .forms import CustomLoginForm, CustomRegisterForm, UploadFileForm
from CustomerStats.exchange_rates import get_usd_to_uah_rate, calculate_totals
from CustomerStats.filtrations import filter_orders
from CustomerStats.views import create_video
from MyDjangoBot.settings import BASE_DIR


def get_client_model():
    return apps.get_model('CustomerStats', 'Client')


class MyLoginView(LoginView):
    template_name = 'CustomerStatsTW/components/authForms/login.html'
    authentication_form = CustomLoginForm
    def get_success_url(self):
        return reverse('Auth:profile')


class RegisterView(CreateView):
    template_name = 'CustomerStatsTW/components/authForms/registration.html'
    form_class = CustomRegisterForm
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
        user = await sync_to_async(lambda: request.user, thread_sensitive=True)()

        client = None
        if await sync_to_async(lambda: user.is_authenticated, thread_sensitive=True)():
            client = await sync_to_async(
                lambda: get_client_model().objects.filter(user=user).first(),
                thread_sensitive=True
            )()

        usd_to_uah = await sync_to_async(get_usd_to_uah_rate)()

        totals, form, query, has_filters = {}, None, "", False
        if client:
            orders_qs = get_client_model().objects.none()
            orders_qs = client.order_set.all()

            orders, form, query, has_filters = await sync_to_async(
                lambda: filter_orders(request, orders_qs)
            )()

            totals = await calculate_totals(orders, usd_to_uah)

        context = {
            "GOOGLE_OAUTH_CLIENT_ID": os.environ.get("GOOGLE_OAUTH_CLIENT_ID"),
            "greeting": "Вітаємо,",
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
            file = form.cleaned_data["file"]
            filename = file.name
            order_time = localtime().astimezone(get_localzone())
            save_dir = pathlib.Path(create_model_path(order_time,
                                                      'username',
                                                      "first_name",
                                                      "last_name",
                                                      18))
            file_path = save_dir / file.name

            async with aiofiles.open(file_path, "wb+") as destination:
                for chunk in file.chunks():
                    await destination.write(chunk)
            await create_video(str(file_path))
            await sync_to_async(lambda: request.user.client.order_set.create(time=order_time,
                                                                             video_path=file_path,
                                                                             volume_mm3=20,
                                                                             price_usd=0))()
            return redirect("Auth:profile")

        context = await self.get_context_data(request, upload_file_form=form)
        return await sync_to_async(
            lambda: render(request, self.template_name, context)
        )()
