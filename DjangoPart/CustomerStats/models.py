from django.db import models
from django.db.models import Sum

class DeliveryType(models.Model):
    class Meta:
        app_label = 'CustomerStats'


    delivery_type = models.CharField(max_length=100)

    def __str__(self):
        return self.delivery_type

class Client(models.Model):
    class Meta:
        app_label = 'CustomerStats'


    delivery_type = models.ForeignKey(DeliveryType, on_delete=models.PROTECT, null=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Order(models.Model):
    class Meta:
        app_label = 'CustomerStats'
    delivery_type = models.ForeignKey(DeliveryType, on_delete=models.PROTECT, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    video_path = models.CharField(max_length=255)
    volume_mm3 = models.FloatField()
    price_usd = models.FloatField()

    def __str__(self):
        return self.name

    @staticmethod
    def sale_by_volume(volume: float):
        sales = {
            0.1: 0,
            0.5: 0.02,
            1: 0.05,
            5: 0.1,
        }
        limits = sorted(sales.keys())
        sale_percent = 0
        for limit in limits:
            if volume >= limit:
                sale_percent = sales[limit]
            else:
                break
        return sale_percent
