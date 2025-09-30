from django.db.models import QuerySet
from .forms import OrderFilterForm

def filter_orders(request, orders: QuerySet):
    form = OrderFilterForm(request.GET or None)
    query = ""

    if form.is_valid():
        query = form.cleaned_data.get("search", "")
        if query:
            orders = orders.filter(video_path__icontains=query)

        if form.cleaned_data.get('start_date') is not None:
            orders = orders.filter(time__date__gte=form.cleaned_data['start_date'])

        if form.cleaned_data.get('end_date') is not None:
            orders = orders.filter(time__date__lte=form.cleaned_data['end_date'])

        if form.cleaned_data.get('min_volume') is not None:
            orders = orders.filter(volume_mm3__gte=form.cleaned_data['min_volume'])
        if form.cleaned_data.get('max_volume') is not None:
            orders = orders.filter(volume_mm3__lte=form.cleaned_data['max_volume'])

        if form.cleaned_data.get('min_price') is not None:
            orders = orders.filter(price_usd__gte=form.cleaned_data['min_price'])
        if form.cleaned_data.get('max_price') is not None:
            orders = orders.filter(price_usd__lte=form.cleaned_data['max_price'])

    has_filters = any(value for key, value in request.GET.items() if value)

    return orders, form, query, has_filters