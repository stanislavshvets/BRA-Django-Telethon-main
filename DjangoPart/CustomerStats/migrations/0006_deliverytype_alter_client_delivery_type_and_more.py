import django
from django.db import migrations, models

def create_delivery_types(apps, schema_editor):
    DeliveryType = apps.get_model("CustomerStats", "DeliveryType")

    # створюємо записи
    for dtype in ["post", "taxi", "courier"]:
        DeliveryType.objects.create(delivery_type=dtype)


def migrate_client_delivery(apps, schema_editor):
    Client = apps.get_model("CustomerStats", "Client")
    Order = apps.get_model("CustomerStats", "Order")
    DeliveryType = apps.get_model("CustomerStats", "DeliveryType")

    # робимо мапу { "post": <DeliveryType об'єкт>, ... }
    mapping = {dt.delivery_type: dt for dt in DeliveryType.objects.all()}

    # переносимо дані для Client
    for client in Client.objects.all():
        if client.delivery_type:  # старе текстове поле
            client.delivery_type_fk = mapping[client.delivery_type]
            client.save(update_fields=["delivery_type_fk"])

    # переносимо дані для Order
    for order in Order.objects.all():
        if order.delivery_type:  # старе текстове поле
            order.delivery_type_fk = mapping[order.delivery_type]
            order.save(update_fields=["delivery_type_fk"])


class Migration(migrations.Migration):

    dependencies = [
        ("CustomerStats", "0005_seed_data"),
    ]

    operations = [
        # 1. створюємо нову таблицю
        migrations.CreateModel(
            name="DeliveryType",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("delivery_type", models.CharField(max_length=100)),
            ],
        ),

        # 2. додаємо тимчасові поля з ForeignKey (null=True)
        migrations.AddField(
            model_name="client",
            name="delivery_type_fk",
            field=models.ForeignKey(
                to="CustomerStats.DeliveryType",
                on_delete=models.PROTECT,
                null=True,
                related_name="+",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="delivery_type_fk",
            field=models.ForeignKey(
                to="CustomerStats.DeliveryType",
                on_delete=models.PROTECT,
                null=True,
                related_name="+",
            ),
        ),

        # 3. створюємо записи у DeliveryType
        migrations.RunPython(create_delivery_types),

        # 4. переносимо дані
        migrations.RunPython(migrate_client_delivery),

        # 5. видаляємо старі поля
        migrations.RemoveField(model_name="client", name="delivery_type"),
        migrations.RemoveField(model_name="order", name="delivery_type"),

        # 6. перейменовуємо нові поля на правильне ім’я
        migrations.RenameField(
            model_name="client",
            old_name="delivery_type_fk",
            new_name="delivery_type",
        ),
        migrations.RenameField(
            model_name="order",
            old_name="delivery_type_fk",
            new_name="delivery_type",
        ),
    ]