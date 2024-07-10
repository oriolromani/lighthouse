# serializers.py

from rest_framework import serializers


class PriceDifferenceSerializer(serializers.Serializer):
    hotel = serializers.IntegerField()
    price = serializers.FloatField()
    currency = serializers.CharField(max_length=3)
    difference = serializers.FloatField()
    arrival_date = serializers.DateField()
