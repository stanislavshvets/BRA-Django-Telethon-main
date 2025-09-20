from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum
from django.db import models
import requests

from .models import Client, Order
from .forms import OrderFilterForm

def get_usd_to_uah_rate():
    url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        for item in data:
            if item.get("cc") == "USD":
                return float(item["rate"])
    except Exception as e:
        print(f"Помилка отримання курсу НБУ: {e}")
    return 42.0

def get_client_orders(client_id: int):
    client = Client.objects.get(pk=client_id)
    orders = Order.objects.filter(client=client).select_related("delivery_type")

    return {
        "Client.name": client.name,
        "Order": [
            {
                "delivery_type": order.delivery_type.delivery_type if order.delivery_type else None,
                "name": order.name,
            }
            for order in orders
        ]
    }

def index(request):
    return render(request, 'CustomerStats/index.html', {
        'clients': Client.objects.all()
    })

def user_stats(request, client_id):
    client = get_object_or_404(Client, pk=client_id)

    query = request.GET.get("q", "")

    orders = Order.objects.filter(client_id=client_id).order_by('-time')
    if query:
        orders = orders.filter(video_path__icontains=query)

    form = OrderFilterForm(request.GET or None)
    if form.is_valid():
        if form.cleaned_data['start_date']:
            orders = orders.filter(time__date__gte=form.cleaned_data['start_date'])
        if form.cleaned_data['end_date']:
            orders = orders.filter(time__date__lte=form.cleaned_data['end_date'])

    usd_to_uah = get_usd_to_uah_rate()

    total_orders = orders.count()
    total_volume = orders.aggregate(Sum("volume_mm3"))["volume_mm3__sum"] or 0
    total_usd = orders.aggregate(Sum("price_usd"))["price_usd__sum"] or 0
    total_uah = total_usd * usd_to_uah

    for o in orders:
        o.price_uah = o.price_usd * usd_to_uah

    return render(request, 'CustomerStats/stats2.html', {
        'client_name': client.name,
        'data': Order.time,
        'orders': orders,
        'form': form,
        'total_orders': total_orders,
        'total_volume': total_volume,
        'total_usd': total_usd,
        'total_uah': round(total_uah, 2),
        'usd_to_uah': usd_to_uah,
        'query': query
    })


def delete_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.delete()
    return redirect(request.META.get("HTTP_REFERER", "customer-stats"))
