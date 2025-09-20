from django.db.models import QuerySet
from .forms import OrderFilterForm


def filter_orders(request, orders: QuerySet):
    query = request.GET.get("q", "")

    if query:
        orders = orders.filter(video_path__icontains=query)

    form = OrderFilterForm(request.GET or None)

    if form.is_valid():
        if form.cleaned_data['start_date']:
            orders = orders.filter(time__date__gte=form.cleaned_data['start_date'])
        if form.cleaned_data['end_date']:
            orders = orders.filter(time__date__lte=form.cleaned_data['end_date'])

        if form.cleaned_data['min_volume'] is not None:
            orders = orders.filter(volume_mm3__gte=form.cleaned_data['min_volume'])
        if form.cleaned_data['max_volume'] is not None:
            orders = orders.filter(volume_mm3__lte=form.cleaned_data['max_volume'])

        if form.cleaned_data['min_price'] is not None:
            orders = orders.filter(price_usd__gte=form.cleaned_data['min_price'])
        if form.cleaned_data['max_price'] is not None:
            orders = orders.filter(price_usd__lte=form.cleaned_data['max_price'])

    has_filters = bool(query or any(v for v in request.GET.values()))

    return orders, form, query, has_filters