# Generated by Django 4.2.17 on 2025-01-07 13:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("django_json_schema", "0001_initial"),
        ("producttypen", "0005_producttype_code_producttype_toegestane_statussen"),
    ]

    operations = [
        migrations.AddField(
            model_name="producttype",
            name="verbruiksobject_schema",
            field=models.ForeignKey(
                blank=True,
                help_text="verbruiksobject schema van het product type.",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="product_typen",
                to="django_json_schema.jsonschema",
                verbose_name="verbruiksobject schema",
            ),
        ),
    ]