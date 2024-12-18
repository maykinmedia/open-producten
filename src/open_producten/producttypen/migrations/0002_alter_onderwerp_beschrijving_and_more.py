# Generated by Django 4.2.16 on 2024-12-09 15:38

import datetime
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import markdownx.models


class Migration(migrations.Migration):

    dependencies = [
        ("producttypen", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="onderwerp",
            name="beschrijving",
            field=markdownx.models.MarkdownxField(
                blank=True,
                default="",
                help_text="Beschrijving van het onderwerp, ondersteund markdown format.",
                verbose_name="beschrijving",
            ),
        ),
        migrations.AlterField(
            model_name="prijs",
            name="actief_vanaf",
            field=models.DateField(
                help_text="De datum vanaf wanneer de prijs actief is.",
                validators=[
                    django.core.validators.MinValueValidator(datetime.date.today)
                ],
                verbose_name="start datum",
            ),
        ),
        migrations.AlterField(
            model_name="producttype",
            name="beschrijving",
            field=markdownx.models.MarkdownxField(
                help_text="Product type beschrijving, ondersteund markdown format.",
                verbose_name="beschrijving",
            ),
        ),
        migrations.AlterField(
            model_name="producttype",
            name="naam",
            field=models.CharField(
                help_text="naam van het product type.",
                max_length=100,
                verbose_name="product type naam",
            ),
        ),
        migrations.AlterField(
            model_name="vraag",
            name="antwoord",
            field=markdownx.models.MarkdownxField(
                help_text="Het antwoord op de vraag, ondersteund markdown format.",
                verbose_name="antwoord",
            ),
        ),
        migrations.AlterField(
            model_name="vraag",
            name="onderwerp",
            field=models.ForeignKey(
                blank=True,
                help_text="Het onderwerp waarbij deze vraag hoort.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="vragen",
                to="producttypen.onderwerp",
                verbose_name="onderwerp",
            ),
        ),
        migrations.AlterField(
            model_name="vraag",
            name="product_type",
            field=models.ForeignKey(
                blank=True,
                help_text="Het product type waarbij deze vraag hoort.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="vragen",
                to="producttypen.producttype",
                verbose_name="Product type",
            ),
        ),
        migrations.AlterField(
            model_name="vraag",
            name="vraag",
            field=models.CharField(
                help_text="De vraag die wordt beantwoord.",
                max_length=250,
                verbose_name="vraag",
            ),
        ),
    ]
