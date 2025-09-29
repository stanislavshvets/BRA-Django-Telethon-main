# CustomerStats/migrations/00xx_executiontype_step1.py
import django.db.models.deletion
from django.db import migrations, models

def seed_execution_types(apps, schema_editor):
    ExecutionType = apps.get_model('CustomerStats', 'ExecutionType')
    for name in ['wax', 'polymer', 'casting', 'laser']:
        ExecutionType.objects.get_or_create(execution_type=name)

def backfill_client_order_fk(apps, schema_editor):
    Client = apps.get_model('CustomerStats', 'Client')
    Order = apps.get_model('CustomerStats', 'Order')
    ExecutionType = apps.get_model('CustomerStats', 'ExecutionType')

    # Build mapping from name -> id
    mapping = {et.execution_type: et.id for et in ExecutionType.objects.all()}

    # Discover which legacy/new fields exist in this historical state
    client_field_names = {f.name for f in Client._meta.get_fields()}
    order_field_names = {f.name for f in Order._meta.get_fields()}

    # Backfill Client (read from legacy string if present, else skip)
    read_client_from_legacy = 'execution_type' in client_field_names
    write_client_fk = 'execution_type_fk' in client_field_names or 'execution_type_fk_id' in client_field_names

    if write_client_fk and read_client_from_legacy:
        for c in Client.objects.all():
            legacy_val = getattr(c, 'execution_type', None)
            if legacy_val and legacy_val in mapping:
                # assign by *_id to avoid extra queries
                setattr(c, 'execution_type_fk_id', mapping[legacy_val])
                c.save(update_fields=['execution_type_fk'])

    # Backfill Order
    read_order_from_legacy = 'execution_type' in order_field_names
    write_order_fk = 'execution_type_fk' in order_field_names or 'execution_type_fk_id' in order_field_names

    if write_order_fk and read_order_from_legacy:
        for o in Order.objects.all():
            legacy_val = getattr(o, 'execution_type', None)
            if legacy_val and legacy_val in mapping:
                setattr(o, 'execution_type_fk_id', mapping[legacy_val])
                o.save(update_fields=['execution_type_fk'])

class Migration(migrations.Migration):
    dependencies = [
        ('CustomerStats', '0010_fill_execution_type'),
    ]
    operations = [
        migrations.CreateModel(
            name='ExecutionType',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('execution_type', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='client',
            name='execution_type_fk',
            field=models.ForeignKey(
                to='CustomerStats.ExecutionType',
                on_delete=django.db.models.deletion.PROTECT,
                null=True,
                related_name='+',
            ),
        ),
        migrations.AddField(
            model_name='order',
            name='execution_type_fk',
            field=models.ForeignKey(
                to='CustomerStats.ExecutionType',
                on_delete=django.db.models.deletion.PROTECT,
                null=True,
                related_name='+',
            ),
        ),
        migrations.RunPython(seed_execution_types, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(backfill_client_order_fk, reverse_code=migrations.RunPython.noop),
    ]
