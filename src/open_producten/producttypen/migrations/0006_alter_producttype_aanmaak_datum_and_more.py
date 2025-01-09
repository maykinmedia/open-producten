# Generated by Django 4.2.17 on 2025-01-09 10:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("producttypen", "0005_producttype_code_producttype_toegestane_statussen"),
    ]

    operations = [
        migrations.AlterField(
            model_name="producttype",
            name="aanmaak_datum",
            field=models.DateTimeField(
                auto_now_add=True,
                help_text="De datum waarop het object is aangemaakt.",
                verbose_name="aanmaak datum",
            ),
        ),
        migrations.AlterField(
            model_name="producttype",
            name="update_datum",
            field=models.DateTimeField(
                auto_now=True,
                help_text="De datum waarop het object voor het laatst is gewijzigd.",
                verbose_name="update datum",
            ),
        ),
        migrations.AlterField(
            model_name="thema",
            name="aanmaak_datum",
            field=models.DateTimeField(
                auto_now_add=True,
                help_text="De datum waarop het object is aangemaakt.",
                verbose_name="aanmaak datum",
            ),
        ),
        migrations.AlterField(
            model_name="thema",
            name="update_datum",
            field=models.DateTimeField(
                auto_now=True,
                help_text="De datum waarop het object voor het laatst is gewijzigd.",
                verbose_name="update datum",
            ),
        ),
    ]
