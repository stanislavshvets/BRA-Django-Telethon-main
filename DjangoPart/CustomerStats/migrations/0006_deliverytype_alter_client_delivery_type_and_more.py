import django
from django.db import migrations, models

def forwards(apps, schema_editor):
    Client = apps.get_model("CustomerStats", "Client")
    Order = apps.get_model("CustomerStats", "Order")
    DeliveryType = apps.get_model("CustomerStats", "DeliveryType")

    # Створюємо унікальні типи доставки
    delivery_map = {}
    for dt in ["post", "taxi", "courier"]:
        obj, _ = DeliveryType.objects.get_or_create(delivery_type=dt)
        delivery_map[dt] = obj

    # Оновлюємо клієнтів
    for client in Client.objects.all():
        if client.delivery_type:
            client.delivery_type = delivery_map.get(client.delivery_type)
            client.save()

    # Оновлюємо замовлення
    for order in Order.objects.all():
        if order.delivery_type:
            order.delivery_type = delivery_map.get(order.delivery_type)
            order.save()


def backwards(apps, schema_editor):
    Client = apps.get_model("CustomerStats", "Client")
    Order = apps.get_model("CustomerStats", "Order")

    # Повертаємо назад у CharField (рядки)
    for client in Client.objects.all():
        if client.delivery_type:
            client.delivery_type = client.delivery_type.delivery_type
            client.save()

    for order in Order.objects.all():
        if order.delivery_type:
            order.delivery_type = order.delivery_type.delivery_type
            order.save()


class Migration(migrations.Migration):

    dependencies = [
        ("CustomerStats", "0005_seed_data"),  # заміни на свою першу міграцію
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delivery_type', models.CharField(max_length=100)),
            ],
        ),
        migrations.AlterField(
            model_name='client',
            name='delivery_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT,
                                    to='CustomerStats.deliverytype'),
        ),
        migrations.AlterField(
            model_name='order',
            name='delivery_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT,
                                    to='CustomerStats.deliverytype'),
        ),
        migrations.RunPython(forwards, backwards),
    ]