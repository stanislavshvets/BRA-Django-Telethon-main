from django.db import models
from django.conf import settings

class DeliveryType(models.Model):
    delivery_type = models.CharField(max_length=100)

    def __str__(self):
        return self.delivery_type

class Client(models.Model):
    delivery_type = models.ForeignKey(DeliveryType, on_delete=models.PROTECT, null=True)
    name = models.CharField(max_length=100)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null = True, blank = True, related_name='client')

    def __str__(self):
        return self.name

class ExecutionType(models.Model):
    execution_type = models.CharField(max_length=100)


class Order(models.Model):
    delivery_type = models.ForeignKey(DeliveryType, on_delete=models.PROTECT, null=True)
    execution_type = models.ForeignKey(ExecutionType, on_delete=models.PROTECT, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    video_path = models.CharField(max_length=255)
    volume_mm3 = models.FloatField()
    price_usd = models.FloatField()

    def __str__(self):
        return self.video_path

    def sale_by_volume(self):
        sales = {
            # Volume lower bound - Sale
            0.1: 0.02,
            0.5: 0.05,
            1: 0.1,
            5: 0.2,
        }
        limits = sorted(sales.keys())
        sale_percent = 0
        for limit in limits:
            if self.volume_mm3 >= limit:
                sale_percent = sales[limit]
            else:
                break
        return sale_percent
