from django.db import migrations
import random


def seed_data(apps, schema_editor):
    Client = apps.get_model("CustomerStats", "Client")
    Order = apps.get_model("CustomerStats", "Order")

    DELIVERY_CHOICES = ["post", "taxi", "courier"]

    # створюємо клієнтів
    clients = [
        Client(name=f"Client {i}", delivery_type=random.choice(DELIVERY_CHOICES))
        for i in range(1, 4)
    ]
    Client.objects.bulk_create(clients)

    # треба заново отримати з бази, бо id після bulk_create не гарантуються
    clients = list(Client.objects.all())

    orders = []
    for client in clients:
        for j in range(1, 4):
            orders.append(
                Order(
                    client=client,
                    name=f"Order {j} for {client.name}",
                    volume_mm3=random.randint(100, 1000),
                    price_usd=round(random.uniform(10, 200), 2),
                    delivery_type=client.delivery_type,
                )
            )

    Order.objects.bulk_create(orders)


def unseed_data(apps, schema_editor):
    Client = apps.get_model("CustomerStats", "Client")
    Order = apps.get_model("CustomerStats", "Order")
    Order.objects.all().delete()
    Client.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("CustomerStats", "0004_client_delivery_type_order_delivery_type"),  # зміни під свій перший файл
    ]

    operations = [
        migrations.RunPython(seed_data, unseed_data),
    ]