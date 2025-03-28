# Generated by Django 4.2.17 on 2025-03-10 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("producten", "0005_product_verbruiksobject"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="dataobject",
            field=models.JSONField(
                blank=True,
                help_text="Dataobject van dit product. Wordt gevalideerd met het `dataobject_schema` uit het product type.",
                null=True,
                verbose_name="dataobject",
            ),
        ),
    ]
