# models.py

from django.db import models


class ExchangeRate(models.Model):
    currency = models.CharField(max_length=3)
    extract_date = models.DateField()
    rate_to_usd = models.FloatField()

    class Meta:
        unique_together = ("currency", "extract_date")
        indexes = [
            models.Index(fields=["currency", "extract_date"]),
        ]
