from datetime import datetime, timedelta

from django.db.models import Min
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Price
from .serializers import PriceSerializer


class PricingDifferenceView(APIView):
    def get(self, request, format=None):
        month = request.query_params.get("month")
        currency = request.query_params.get("currency")
        hotels = request.query_params.getlist("hotels")
        years_ago = int(request.query_params.get("years_ago"))
        cancellable = request.query_params.get("cancellable", "true").lower() == "true"

        if not month or not currency or not hotels or not years_ago:
            return Response(
                {"detail": "Missing required parameters"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        start_date = datetime.strptime(month, "%Y-%m")
        end_date = start_date + timedelta(days=31)
        historical_date = start_date - timedelta(days=365 * years_ago)

        response_data = []

        for hotel_id in hotels:
            current_prices = (
                Price.objects.filter(
                    hotel_id=hotel_id,
                    date__range=[start_date, end_date],
                    currency=currency,
                    cancellable=cancellable,
                )
                .values("date")
                .annotate(price=Min("price"))
            )

            historical_prices = (
                Price.objects.filter(
                    hotel_id=hotel_id,
                    date__range=[historical_date, historical_date + timedelta(days=31)],
                    currency=currency,
                    cancellable=cancellable,
                )
                .values("date")
                .annotate(price=Min("price"))
            )

            historical_prices_dict = {
                price["date"]: price["price"] for price in historical_prices
            }

            for current_price in current_prices:
                arrival_date = current_price["date"]
                current_price_value = current_price["price"]
                historical_price_value = historical_prices_dict.get(arrival_date, None)

                if historical_price_value is not None:
                    difference = current_price_value - historical_price_value
                    response_data.append(
                        {
                            "hotel": hotel_id,
                            "price": current_price_value,
                            "currency": currency,
                            "difference": difference,
                            "arrival_date": arrival_date,
                        }
                    )

        return Response(
            {"prices": PriceSerializer(response_data, many=True).data},
            status=status.HTTP_200_OK,
        )
