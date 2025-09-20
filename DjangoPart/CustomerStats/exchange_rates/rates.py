import requests
from django.db.models import QuerySet, Sum


def get_usd_to_uah_rate() -> float:
    url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        for item in data:
            if item.get("cc") == "USD":
                return float(item["rate"])
    except Exception as e:
        print(f"Помилка отримання курсу НБУ: {e}")
    return 42.0


def calculate_totals(orders: QuerySet, usd_to_uah: float):
    total_orders = orders.count()
    total_volume = orders.aggregate(Sum("volume_mm3"))["volume_mm3__sum"] or 0
    total_usd = orders.aggregate(Sum("price_usd"))["price_usd__sum"] or 0
    total_uah = total_usd * usd_to_uah

    for o in orders:
        o.price_uah = o.price_usd * usd_to_uah

    return {
        "total_orders": total_orders,
        "total_volume": total_volume,
        "total_usd": total_usd,
        "total_uah": round(total_uah, 2),
    }