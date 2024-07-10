from datetime import datetime, timedelta
from unittest.mock import patch

from django.urls import reverse
from django.utils.dateparse import parse_date
from rest_framework import status
from rest_framework.test import APITestCase

from pricing.models import ExchangeRate
from pricing.views import PricingDifferenceAPIView


class PricingDifferenceAPITestCase(APITestCase):
    def setUp(self):
        self.url = reverse("pricing-difference")

    @patch("pricing.views.ExchangeRate.objects.get")
    @patch("pricing.views.PricingDifferenceAPIView.fetch_prices_from_bigtable")
    @patch("pricing.views.PricingDifferenceAPIView.process_prices")
    def test_pricing_difference(self, mock_process_prices, mock_fetch_prices, mock_get_exchange_rate):
        # Mock data
        current_rate = 1.2
        historical_rate = 1.1
        processed_data = [
            {
                "hotel": 1,
                "price": 100.0,
                "currency": "USD",
                "difference": 10.0,
                "arrival_date": "2023-12-01",
            },
            {
                "hotel": 1,
                "price": 95.0,
                "currency": "USD",
                "difference": 8.0,
                "arrival_date": "2023-12-02",
            },
        ]

        # Mock ExchangeRate model
        mock_get_exchange_rate.side_effect = lambda **kwargs: ExchangeRate(rate_to_usd=current_rate) if kwargs["extract_date"] == parse_date("2023-12-01") else ExchangeRate(rate_to_usd=historical_rate)

        # Mock fetch_prices_from_bigtable
        mock_fetch_prices.return_value = {
            1: {
                "2023-12-01": 100.0,
                "2023-12-02": 95.0,
            }
        }

        # Mock process_prices
        mock_process_prices.return_value = processed_data

        # Make request
        response = self.client.get(
            self.url, {"month": "2023-12", "currency": "USD", "hotels": [1], "years_ago": 1}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(processed_data))

    @patch("pricing.views.ExchangeRate.objects.get")
    def test_exchange_rate_not_found(self, mock_get_exchange_rate):
        mock_get_exchange_rate.side_effect = ExchangeRate.DoesNotExist

        response = self.client.get(
            self.url, {"month": "2023-12", "currency": "USD", "hotels": [1], "years_ago": 1}
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch("pricing.views.ExchangeRate.objects.get")
    def test_invalid_currency(self, mock_get_exchange_rate):
        mock_get_exchange_rate.side_effect = ExchangeRate.DoesNotExist

        response = self.client.get(
            self.url, {"month": "2023-12", "currency": "EUR", "hotels": [1], "years_ago": 1}
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
