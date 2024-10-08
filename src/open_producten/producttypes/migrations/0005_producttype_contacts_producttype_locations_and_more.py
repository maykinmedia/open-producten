# Generated by Django 4.2.13 on 2024-09-04 09:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("locations", "0001_initial"),
        ("producttypes", "0004_alter_priceoption_amount"),
    ]

    operations = [
        migrations.AddField(
            model_name="producttype",
            name="contacts",
            field=models.ManyToManyField(
                blank=True,
                help_text="The contacts responsible for the product",
                related_name="products",
                to="locations.contact",
                verbose_name="Contacts",
            ),
        ),
        migrations.AddField(
            model_name="producttype",
            name="locations",
            field=models.ManyToManyField(
                blank=True,
                help_text="Locations where the product is available at.",
                related_name="products",
                to="locations.location",
                verbose_name="Locations",
            ),
        ),
        migrations.AddField(
            model_name="producttype",
            name="organisations",
            field=models.ManyToManyField(
                blank=True,
                help_text="Organisations which provides this product",
                related_name="products",
                to="locations.organisation",
                verbose_name="Organisations",
            ),
        ),
    ]
