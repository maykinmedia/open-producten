# Generated by Django 4.2.17 on 2025-02-07 15:49

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("producten", "0004_product_frequentie_product_prijs"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="prijs",
            field=models.DecimalField(
                decimal_places=2,
                help_text="De prijs van het product.",
                max_digits=8,
                validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
                verbose_name="prijs",
            ),
        ),
    ]
