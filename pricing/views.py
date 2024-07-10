# views.py

import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.db.models import Q
from django.utils.dateparse import parse_date
from google.cloud import bigtable
from google.cloud.bigtable.row_filters import ColumnRangeFilter, RowFilterChain
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from pricing.models import ExchangeRate
from pricing.serializers import PriceDifferenceSerializer

logger = logging.getLogger(__name__)


class PricingDifferenceAPIView(APIView):
    def get(self, request):
        start_time = datetime.now()

        # Extract query parameters
        month = request.query_params.get("month")
        currency = request.query_params.get("currency")
        hotels = request.query_params.getlist("hotels")
        years_ago = int(request.query_params.get("years_ago"))
        cancellable = request.query_params.get("cancellable", "true").lower() == "true"

        # Validate parameters
        if not (month and currency and hotels and years_ago):
            return Response(
                {"detail": "Missing required parameters."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Calculate date ranges
        start_date = parse_date(month + "-01")
        if not start_date:
            return Response(
                {"detail": "Invalid month format."}, status=status.HTTP_400_BAD_REQUEST
            )

        end_date = start_date + timedelta(days=31)
        historical_start_date = start_date - timedelta(days=years_ago * 365)
        historical_end_date = historical_start_date + timedelta(days=31)

        # Fetch exchange rates
        current_rate = self.fetch_exchange_rate(currency, start_date)
        historical_rate = self.fetch_exchange_rate(currency, historical_start_date)

        if current_rate is None or historical_rate is None:
            return Response(
                {"detail": "Exchange rate not found for the given dates."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Fetch prices from Bigtable
        current_prices = self.fetch_prices_from_bigtable(
            hotels, start_date, end_date, currency, cancellable
        )
        historical_prices = self.fetch_prices_from_bigtable(
            hotels, historical_start_date, historical_end_date, currency, cancellable
        )

        # Process prices
        processed_data = self.process_prices(
            current_prices, historical_prices, current_rate, historical_rate, currency
        )

        # Serialize the response data
        serializer = PriceDifferenceSerializer(processed_data, many=True)

        # Log request duration
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Request processed in {duration} seconds")

        return Response(serializer.data, status=status.HTTP_200_OK)

    def fetch_exchange_rate(self, currency, date):
        try:
            exchange_rate = ExchangeRate.objects.get(
                currency=currency, extract_date=date
            )
            return exchange_rate.rate_to_usd
        except ExchangeRate.DoesNotExist:
            return None

    def fetch_prices_from_bigtable(
        self, hotels, start_date, end_date, currency, cancellable
    ):
        client = bigtable.Client()
        instance = client.instance(settings.BIGTABLE_INSTANCE_ID)
        table = instance.table(settings.BIGTABLE_TABLE_ID)
        prices = {}

        for hotel in hotels:
            prices[hotel] = {}
            row_filter = RowFilterChain(
                filters=[
                    ColumnRangeFilter(
                        "arrival_date", start_date.isoformat(), end_date.isoformat()
                    )
                ]
            )
            partial_rows = table.read_rows(
                start_key=str(hotel), end_key=str(hotel) + "\0", filter_=row_filter
            )

            for row in partial_rows:
                arrival_date = row.cell_value("arrival_date", "cf1")
                price = row.cell_value("price", "cf1")
                if price:
                    prices[hotel][arrival_date] = float(price)

        return prices

    def process_prices(
        self, current_prices, historical_prices, current_rate, historical_rate, currency
    ):
        response_data = []

        for hotel, dates in current_prices.items():
            for arrival_date, current_price in dates.items():
                historical_price = historical_prices.get(hotel, {}).get(arrival_date)

                if historical_price is not None:
                    current_price_usd = (
                        current_price / current_rate
                        if currency != "USD"
                        else current_price
                    )
                    historical_price_usd = (
                        historical_price / historical_rate
                        if currency != "USD"
                        else historical_price
                    )
                    price_difference = current_price_usd - historical_price_usd

                    response_data.append(
                        {
                            "hotel": hotel,
                            "price": current_price_usd,
                            "currency": "USD",
                            "difference": price_difference,
                            "arrival_date": arrival_date,
                        }
                    )

        return response_data
