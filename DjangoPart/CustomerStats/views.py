import aiohttp
from asgiref.sync import async_to_sync, sync_to_async
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect, aget_object_or_404
from django.views.generic import TemplateView

from .models import Client, Order
from .filtrations import filter_orders
from .exchange_rates import get_usd_to_uah_rate, calculate_totals

def index(request):
    return render(request, 'CustomerStatsTW/components/AdminPage/index.html', {
        'clients': Client.objects.all()
    })

async def user_stats(request, client_id):
    client = await aget_object_or_404(Client, pk=client_id)

    orders = await sync_to_async(lambda: Order.objects.filter(client_id=client_id).order_by('-time'))()
    orders, form, query, has_filters = filter_orders(request, orders)

    usd_to_uah = get_usd_to_uah_rate()
    totals = await calculate_totals(orders, usd_to_uah)

    return await sync_to_async(
        lambda: render(request, 'CustomerStatsTW/components/AdminPage/stats.html', {
        'is_user_authenticated': request.user.is_authenticated,
        'client_name': client.name,
        'orders': orders,
        'form': form,
        'usd_to_uah': usd_to_uah,
        'query': query,
        'has_filters': has_filters,
        'client': client,
        **totals,
    }))()


async def delete_order(request, pk):
    async def _get_order():
        return list(request.user.client.order_set.filter(pk=pk).values_list("pk", flat=True))

    one_order_list = await sync_to_async(_get_order, thread_sensitive=True)()
    if not one_order_list:
        raise Http404

    await sync_to_async(
        lambda: request.user.client.order_set.filter(pk=pk).delete(),
        thread_sensitive=True
    )()

    return redirect(request.META.get("HTTP_REFERER", "customer-stats"))

async def create_video(path):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post('http://localhost:8081/render', json={'obj_path': path}) as response:
                response.raise_for_status()
                data = await response.json()
                job_id = data.get('job_id')
                print(f"Render job submitted successfully. Job ID: {job_id}")
                # Here you would typically save the job_id to the Order model
                return job_id
        except aiohttp.ClientError as e:
            print(f"Error submitting render job: {e}")
            return None


class About(TemplateView):
    template_name = 'CustomerStatsTW/components/aboutUsPage/about.html'
