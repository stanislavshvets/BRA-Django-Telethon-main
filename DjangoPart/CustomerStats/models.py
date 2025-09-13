from django.db import models

# Create your models here.

class Client(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    name = models.FilePathField()
    volume_mm3 = models.FloatField()
    price_usd = models.FloatField()

    def __str__(self):
        return self.name