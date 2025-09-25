from unittest.mock import patch
from django.test import TestCase
from .exchange_rates.rates import get_usd_to_uah_rate
from .models import Order, DeliveryType


class ThirdPartyTest(TestCase):
    @patch('requests.get')
    def test_get_exchange_rate(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [
            {"cc": "EUR", "rate": 40.0},
            {"cc": "USD", "rate": 36.57},
            {"cc": "GBP", "rate": 45.0},
        ]

        rate = get_usd_to_uah_rate()
        self.assertAlmostEqual(rate, 36.57, places=2)
        mock_get.assert_called_once_with(
            "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json",
            timeout=5
        )
        
class OrdersTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.order = Order.objects.create(
            volume_mm3=0.05,
            price_usd=100,
            video_path='test/path',
            client_id=1
        )

    def test_sale_calc(self):
        test_cases = [
            (0.05, 0),  # Below first threshold
            (0.1, 0.02),  # At first threshold
            (0.3, 0.02),  # Between first and second threshold
            (0.5, 0.05),  # At second threshold
            (0.8, 0.05),  # Between second and third threshold
            (1.0, 0.1),  # At third threshold
            (3.0, 0.1),  # Between third and fourth threshold
            (5.0, 0.2),  # At fourth threshold
            (10.0, 0.2),  # Above all thresholds
        ]

        for volume, expected_sale in test_cases:
            order = Order(volume_mm3=volume, price_usd=100)
            self.assertAlmostEqual(order.sale_by_volume(), expected_sale, msg=f"Failed for volume {volume}")
        
        
