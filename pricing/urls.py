# urls.py

from django.urls import path

from pricing.views import PricingDifferenceAPIView

urlpatterns = [
    path(
        "pricing/pre_corona_difference/",
        PricingDifferenceAPIView.as_view(),
        name="pricing-difference",
    ),
]
