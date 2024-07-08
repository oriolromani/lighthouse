from rest_framework import serializers

from .models import Price


class PriceSerializer(serializers.Serializer):
    hotel = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=3)
    difference = serializers.DecimalField(max_digits=10, decimal_places=2)
    arrival_date = serializers.DateField()
