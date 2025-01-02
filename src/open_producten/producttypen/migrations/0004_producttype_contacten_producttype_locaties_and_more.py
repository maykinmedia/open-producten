# Generated by Django 4.2.17 on 2024-12-30 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("locaties", "0001_initial"),
        ("producttypen", "0003_thema_remove_producttype_onderwerpen_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="producttype",
            name="contacten",
            field=models.ManyToManyField(
                blank=True,
                help_text="De contacten verantwoordelijk voor het product type.",
                related_name="product_typen",
                to="locaties.contact",
                verbose_name="contacten",
            ),
        ),
        migrations.AddField(
            model_name="producttype",
            name="locaties",
            field=models.ManyToManyField(
                blank=True,
                help_text="De locaties waar het product beschikbaar is.",
                related_name="product_typen",
                to="locaties.locatie",
                verbose_name="locaties",
            ),
        ),
        migrations.AddField(
            model_name="producttype",
            name="organisaties",
            field=models.ManyToManyField(
                blank=True,
                help_text="organisaties die dit het product aanbieden.",
                related_name="product_typen",
                to="locaties.organisatie",
                verbose_name="organisaties",
            ),
        ),
    ]