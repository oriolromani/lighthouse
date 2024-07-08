from django.db import models


class Hotel(models.Model):
    name = models.CharField(max_length=255)


class Price(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    cancellable = models.BooleanField(default=True)
