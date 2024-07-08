from django.urls import path

from pricing.views import PricingDifferenceView

urlpatterns = [
    path(
        "pricing/pre_corona_difference/",
        PricingDifferenceView.as_view(),
        name="pre_corona_difference",
    )
]
