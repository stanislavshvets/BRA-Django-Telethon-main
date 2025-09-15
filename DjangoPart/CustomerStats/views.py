from django.http import HttpResponse
from django.shortcuts import render

from .models import Client, Order


# Create your views here.
def index(request):
    return render(request, 'CustomerStats/index.html', {
        'clients': Client.objects.all()
    })

def user_stats(request, client_id):
    return render(request, 'CustomerStats/stats.html', {
        'client_name': Client.objects.get(pk=client_id).name,
        'orders': Order.objects.filter(client_id=client_id).order_by('-time')
    })
