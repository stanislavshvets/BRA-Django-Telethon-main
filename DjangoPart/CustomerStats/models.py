from django.db import models

class DeliveryType(models.Model):
    delivery_type = models.CharField(max_length=100)

    def __str__(self):
        return self.delivery_type

class Client(models.Model):
    delivery_type = models.ForeignKey(DeliveryType, on_delete=models.PROTECT, null=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Order(models.Model):
    delivery_type = models.ForeignKey(DeliveryType, on_delete=models.PROTECT, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    volume_mm3 = models.FloatField()
    price_usd = models.FloatField()

    def __str__(self):
        return self.name