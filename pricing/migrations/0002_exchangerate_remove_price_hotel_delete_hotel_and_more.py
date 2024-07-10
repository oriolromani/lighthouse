# Generated by Django 4.2.13 on 2024-07-10 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pricing", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExchangeRate",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("currency", models.CharField(max_length=3)),
                ("extract_date", models.DateField()),
                ("rate_to_usd", models.FloatField()),
            ],
        ),
        migrations.RemoveField(
            model_name="price",
            name="hotel",
        ),
        migrations.DeleteModel(
            name="Hotel",
        ),
        migrations.DeleteModel(
            name="Price",
        ),
        migrations.AddIndex(
            model_name="exchangerate",
            index=models.Index(
                fields=["currency", "extract_date"],
                name="pricing_exc_currenc_49a929_idx",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="exchangerate",
            unique_together={("currency", "extract_date")},
        ),
    ]
