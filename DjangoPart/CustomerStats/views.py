from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView

from .models import Client, Order
from .filtrations import filter_orders
from .exchange_rates import get_usd_to_uah_rate, calculate_totals

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
    return render(request, 'CustomerStatsTW/components/index.html', {
        'clients': Client.objects.all()
    })

def user_stats(request, client_id):
    client = get_object_or_404(Client, pk=client_id)

    orders = Order.objects.filter(client_id=client_id).order_by('-time')
    orders, form, query, has_filters = filter_orders(request, orders)

    usd_to_uah = get_usd_to_uah_rate()
    totals = calculate_totals(orders, usd_to_uah)

    return render(request, 'CustomerStatsTW/components/stats.html', {
        'client_name': client.name,
        'orders': orders,
        'form': form,
        'usd_to_uah': usd_to_uah,
        'query': query,
        'has_filters': has_filters,
        'client': client,
        **totals,
    })


def delete_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.delete()
    return redirect(request.META.get("HTTP_REFERER", "customer-stats"))

class About(TemplateView):
    template_name = 'CustomerStatsTW/components/about.html'
