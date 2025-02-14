# Generated by Django 4.2.17 on 2025-02-04 09:59

from django.db import migrations, models
import django.db.models.deletion
import parler.fields
import parler.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        (
            "producttypen",
            "0005_producttype_code_producttype_toegestane_statussen_and_more",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="ContentElement",
            fields=[
                (
                    "order",
                    models.PositiveIntegerField(
                        db_index=True, editable=False, verbose_name="order"
                    ),
                ),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
            ],
            options={
                "verbose_name": "content element",
                "verbose_name_plural": "content elementen",
                "ordering": ("product_type", "order"),
            },
            bases=(parler.models.TranslatableModel, models.Model),
        ),
        migrations.CreateModel(
            name="ContentElementTranslation",
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
                (
                    "language_code",
                    models.CharField(
                        db_index=True, max_length=15, verbose_name="Language"
                    ),
                ),
                (
                    "content",
                    models.TextField(
                        help_text="De content van dit content element",
                        verbose_name="content",
                    ),
                ),
                (
                    "master",
                    parler.fields.TranslationsForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translations",
                        to="producttypen.contentelement",
                    ),
                ),
            ],
            options={
                "verbose_name": "content element Translation",
                "db_table": "producttypen_contentelement_translation",
                "db_tablespace": "",
                "managed": True,
                "default_permissions": (),
                "unique_together": {("language_code", "master")},
            },
            bases=(parler.models.TranslatableModel, models.Model),
        ),
        migrations.CreateModel(
            name="ContentLabel",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("naam", models.CharField(max_length=255, unique=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ProductTypeTranslation",
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
                (
                    "language_code",
                    models.CharField(
                        db_index=True, max_length=15, verbose_name="Language"
                    ),
                ),
                (
                    "samenvatting",
                    models.TextField(
                        default="",
                        help_text="Korte samenvatting van het product type.",
                        verbose_name="samenvatting",
                    ),
                ),
                (
                    "naam",
                    models.CharField(
                        help_text="naam van het product type.",
                        max_length=255,
                        verbose_name="product type naam",
                    ),
                ),
            ],
            options={
                "verbose_name": "Product type Translation",
                "db_table": "producttypen_producttype_translation",
                "db_tablespace": "",
                "managed": True,
                "default_permissions": (),
            },
            bases=(parler.models.TranslatableModel, models.Model),
        ),
        migrations.RemoveField(
            model_name="producttype",
            name="beschrijving",
        ),
        migrations.RemoveField(
            model_name="producttype",
            name="naam",
        ),
        migrations.RemoveField(
            model_name="producttype",
            name="samenvatting",
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
        migrations.DeleteModel(
            name="Vraag",
        ),
        migrations.AddField(
            model_name="producttypetranslation",
            name="master",
            field=parler.fields.TranslationsForeignKey(
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="translations",
                to="producttypen.producttype",
            ),
        ),
        migrations.AddField(
            model_name="contentelement",
            name="labels",
            field=models.ManyToManyField(
                blank=True,
                help_text="De labels van dit content element",
                related_name="content_elements",
                to="producttypen.contentlabel",
                verbose_name="labels",
            ),
        ),
        migrations.AddField(
            model_name="contentelement",
            name="product_type",
            field=models.ForeignKey(
                help_text="Het product type van dit content element",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="content_elementen",
                to="producttypen.producttype",
                verbose_name="label",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="producttypetranslation",
            unique_together={("language_code", "master")},
        ),
    ]
