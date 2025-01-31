# Generated by Django 4.2.17 on 2025-01-31 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("producttypen", "0012_delete_vraag"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contentlabel",
            name="naam",
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name="link",
            name="naam",
            field=models.CharField(
                help_text="Naam van de link.", max_length=255, verbose_name="naam"
            ),
        ),
        migrations.AlterField(
            model_name="prijsoptie",
            name="beschrijving",
            field=models.CharField(
                help_text="Korte beschrijving van de optie.",
                max_length=255,
                verbose_name="beschrijving",
            ),
        ),
        migrations.AlterField(
            model_name="producttype",
            name="code",
            field=models.CharField(
                help_text="code van het product type.",
                max_length=255,
                unique=True,
                verbose_name="code",
            ),
        ),
        migrations.AlterField(
            model_name="producttypetranslation",
            name="naam",
            field=models.CharField(
                help_text="naam van het product type.",
                max_length=255,
                verbose_name="product type naam",
            ),
        ),
        migrations.AlterField(
            model_name="producttypetranslation",
            name="samenvatting",
            field=models.TextField(
                default="",
                help_text="Korte samenvatting van het product type.",
                verbose_name="samenvatting",
            ),
        ),
        migrations.AlterField(
            model_name="thema",
            name="beschrijving",
            field=models.TextField(
                blank=True,
                default="",
                help_text="Beschrijving van het thema, ondersteund markdown format.",
                verbose_name="beschrijving",
            ),
        ),
        migrations.AlterField(
            model_name="thema",
            name="naam",
            field=models.CharField(
                help_text="Naam van het thema.", max_length=255, verbose_name="naam"
            ),
        ),
        migrations.AlterField(
            model_name="uniformeproductnaam",
            name="naam",
            field=models.CharField(
                help_text="Uniforme product naam",
                max_length=255,
                unique=True,
                verbose_name="naam",
            ),
        ),
    ]
