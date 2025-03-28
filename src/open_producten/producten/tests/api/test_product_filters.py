from datetime import date
from decimal import Decimal
from uuid import uuid4

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from freezegun import freeze_time
from rest_framework import status
from rest_framework.exceptions import ErrorDetail

from open_producten.producten.models.product import PrijsFrequentieChoices
from open_producten.producten.tests.factories import ProductFactory
from open_producten.producttypen.models.producttype import ProductStateChoices
from open_producten.producttypen.tests.factories import (
    JsonSchemaFactory,
    ProductTypeFactory,
)
from open_producten.utils.tests.cases import BaseApiTestCase


class TestProductFilters(BaseApiTestCase):

    path = reverse_lazy("product-list")

    def test_gepubliceerd_filter(self):
        ProductFactory.create(gepubliceerd=True)
        ProductFactory.create(gepubliceerd=False)

        response = self.client.get(self.path, {"gepubliceerd": "true"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["gepubliceerd"], True)

    def test_status_filter(self):
        ProductFactory.create(status=ProductStateChoices.INITIEEL)
        ProductFactory.create(status=ProductStateChoices.GEREED)

        response = self.client.get(self.path, {"status": "initieel"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["status"], "initieel")

    def test_frequentie_filter(self):
        ProductFactory.create(frequentie=PrijsFrequentieChoices.EENMALIG)
        ProductFactory.create(frequentie=PrijsFrequentieChoices.MAANDELIJKS)

        response = self.client.get(self.path, {"frequentie": "eenmalig"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["frequentie"], "eenmalig")

    def test_prijs_filter(self):
        ProductFactory.create(prijs=Decimal("10"))
        ProductFactory.create(prijs=Decimal("20.99"))

        with self.subTest("exact"):
            response = self.client.get(self.path, {"prijs": "20.99"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(response.data["results"][0]["prijs"], "20.99")

        with self.subTest("lte"):
            response = self.client.get(self.path, {"prijs__lte": "20"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(response.data["results"][0]["prijs"], "10.00")

        with self.subTest("gte"):
            response = self.client.get(self.path, {"prijs__gte": "20"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(response.data["results"][0]["prijs"], "20.99")

    def test_product_type_code_filter(self):
        ProductFactory.create(product_type__code="123")
        ProductFactory.create(product_type__code="8234098q2730492873")

        response = self.client.get(
            self.path, {"product_type__code": "8234098q2730492873"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["product_type"]["code"], "8234098q2730492873"
        )

    def test_product_type_upn_filter(self):
        ProductFactory.create(
            product_type__uniforme_product_naam__naam="parkeervergunning"
        )
        ProductFactory.create(product_type__uniforme_product_naam__naam="aanbouw")

        response = self.client.get(
            self.path, {"uniforme_product_naam": "parkeervergunning"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["product_type"]["uniforme_product_naam"],
            "parkeervergunning",
        )

    def test_product_type_id_filter(self):
        product_type_id = uuid4()
        ProductFactory.create(product_type__id=product_type_id)
        ProductFactory.create(product_type__id=uuid4())

        response = self.client.get(self.path + f"?product_type__id={product_type_id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["product_type"]["id"], str(product_type_id)
        )

    def test_product_type_naam_filter(self):
        product_type_id = uuid4()
        ProductFactory.create(
            product_type__naam="parkeervergunning", product_type__id=product_type_id
        )
        ProductFactory.create(product_type__naam="aanbouw")

        response = self.client.get(
            self.path, {"product_type__naam": "parkeervergunning"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["product_type"]["id"], str(product_type_id)
        )

    def test_start_datum_filter(self):
        ProductFactory.create(start_datum=date(2024, 6, 7))
        ProductFactory.create(start_datum=date(2025, 6, 7))

        with self.subTest("exact"):
            response = self.client.get(self.path, {"start_datum": "2024-06-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(response.data["results"][0]["start_datum"], "2024-06-07")

        with self.subTest("lte"):
            response = self.client.get(self.path, {"start_datum__lte": "2024-07-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(response.data["results"][0]["start_datum"], "2024-06-07")

        with self.subTest("gte"):
            response = self.client.get(self.path, {"start_datum__gte": "2025-04-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(response.data["results"][0]["start_datum"], "2025-06-07")

    def test_eind_datum_filter(self):
        ProductFactory.create(eind_datum=date(2024, 6, 7))
        ProductFactory.create(eind_datum=date(2025, 6, 7))

        with self.subTest("exact"):
            response = self.client.get(self.path, {"eind_datum": "2024-06-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(response.data["results"][0]["eind_datum"], "2024-06-07")

        with self.subTest("lte"):
            response = self.client.get(self.path, {"eind_datum__lte": "2024-07-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(response.data["results"][0]["eind_datum"], "2024-06-07")

        with self.subTest("gte"):
            response = self.client.get(self.path, {"eind_datum__gte": "2025-04-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(response.data["results"][0]["eind_datum"], "2025-06-07")

    def test_aanmaak_datum_filter(self):
        with freeze_time("2024-06-07"):
            ProductFactory.create()
        with freeze_time("2025-06-07"):
            ProductFactory.create()

        with self.subTest("exact"):
            response = self.client.get(
                self.path, {"aanmaak_datum": "2024-06-07T00:00:00+00:00"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["aanmaak_datum"],
                "2024-06-07T02:00:00+02:00",
            )

        with self.subTest("lte"):
            response = self.client.get(self.path, {"aanmaak_datum__lte": "2024-07-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["aanmaak_datum"],
                "2024-06-07T02:00:00+02:00",
            )

        with self.subTest("gte"):
            response = self.client.get(self.path, {"aanmaak_datum__gte": "2025-04-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["aanmaak_datum"],
                "2025-06-07T02:00:00+02:00",
            )

    def test_update_datum_filter(self):
        with freeze_time("2024-06-07"):
            ProductFactory.create()
        with freeze_time("2025-06-07"):
            ProductFactory.create()

        with self.subTest("exact"):
            response = self.client.get(
                self.path, {"update_datum": "2024-06-07T00:00:00+00:00"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["update_datum"], "2024-06-07T02:00:00+02:00"
            )

        with self.subTest("lte"):
            response = self.client.get(self.path, {"update_datum__lte": "2024-07-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["update_datum"], "2024-06-07T02:00:00+02:00"
            )

        with self.subTest("gte"):
            response = self.client.get(self.path, {"update_datum__gte": "2025-04-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["update_datum"], "2025-06-07T02:00:00+02:00"
            )

    def test_dataobject_attr_string_filters(self):
        schema = {
            "type": "object",
            "properties": {"naam": {"type": "string"}},
            "required": ["naam"],
        }

        ProductFactory(
            product_type=ProductTypeFactory.create(
                dataobject_schema=JsonSchemaFactory(schema=schema)
            ),
            dataobject={"naam": "test"},
        )

        ProductFactory(
            product_type=ProductTypeFactory.create(
                dataobject_schema=JsonSchemaFactory(schema=schema)
            ),
            dataobject={"naam": "abc"},
        )

        with self.subTest("exact"):
            response = self.client.get(
                self.path, {"dataobject_attr": "naam__exact__test"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(response.data["results"][0]["dataobject"]["naam"], "test")

        with self.subTest("icontains"):
            response = self.client.get(
                self.path, {"dataobject_attr": "naam__icontains__st"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(response.data["results"][0]["dataobject"]["naam"], "test")

        with self.subTest("in"):
            response = self.client.get(
                self.path, {"dataobject_attr": "naam__in__test|abc"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 2)

        for op in ["gt", "gte", "lt", "lte"]:
            with self.subTest(op):
                response = self.client.get(
                    self.path, {"dataobject_attr": f"naam__{op}__abc"}
                )

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verbruiksobject_attr_string_filters(self):
        schema = {
            "type": "object",
            "properties": {"naam": {"type": "string"}},
            "required": ["naam"],
        }

        ProductFactory(
            product_type=ProductTypeFactory.create(
                verbruiksobject_schema=JsonSchemaFactory(schema=schema)
            ),
            verbruiksobject={"naam": "test"},
        )

        ProductFactory(
            product_type=ProductTypeFactory.create(
                verbruiksobject_schema=JsonSchemaFactory(schema=schema)
            ),
            verbruiksobject={"naam": "abc"},
        )

        with self.subTest("exact"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "naam__exact__test"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["verbruiksobject"]["naam"], "test"
            )

        with self.subTest("icontains"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "naam__icontains__st"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["verbruiksobject"]["naam"], "test"
            )

        with self.subTest("in"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "naam__in__test|abc"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 2)

        for op in ["gt", "gte", "lt", "lte"]:
            with self.subTest(op):
                response = self.client.get(
                    self.path, {"verbruiksobject_attr": f"naam__{op}__abc"}
                )

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verbruiksobject_attr_numeric_filters(self):
        schema = {
            "type": "object",
            "properties": {"leeftijd": {"type": "number"}},
            "required": ["leeftijd"],
        }

        ProductFactory(
            product_type=ProductTypeFactory.create(
                verbruiksobject_schema=JsonSchemaFactory(schema=schema)
            ),
            verbruiksobject={"leeftijd": 30},
        )

        ProductFactory(
            product_type=ProductTypeFactory.create(
                verbruiksobject_schema=JsonSchemaFactory(schema=schema)
            ),
            verbruiksobject={"leeftijd": 50},
        )

        with self.subTest("exact"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "leeftijd__exact__30"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["verbruiksobject"]["leeftijd"], 30.0
            )

        with self.subTest("icontains"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "leeftijd__icontains__30"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["verbruiksobject"]["leeftijd"], 30
            )

        with self.subTest("in"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "leeftijd__in__30|50"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 2)

        with self.subTest("gt"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "leeftijd__gt__40"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["verbruiksobject"]["leeftijd"], 50
            )

        with self.subTest("gte"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "leeftijd__gte__50"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["verbruiksobject"]["leeftijd"], 50
            )

        with self.subTest("lt"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "leeftijd__lt__40"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["verbruiksobject"]["leeftijd"], 30
            )

        with self.subTest("lte"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "leeftijd__lte__30"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["verbruiksobject"]["leeftijd"], 30
            )

    def test_verbruiksobject_attr_date_filters(self):
        schema = {
            "type": "object",
            "properties": {"datum": {"type": "date"}},
            "required": ["datum"],
        }

        ProductFactory(
            product_type=ProductTypeFactory.create(
                verbruiksobject_schema=JsonSchemaFactory(schema=schema)
            ),
            verbruiksobject={"datum": "2024-10-10"},
        )

        ProductFactory(
            product_type=ProductTypeFactory.create(
                verbruiksobject_schema=JsonSchemaFactory(schema=schema)
            ),
            verbruiksobject={"datum": "2025-10-10"},
        )

        with self.subTest("none"):
            response = self.client.get(self.path)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.subTest("exact"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "datum__exact__2024-10-10"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["verbruiksobject"]["datum"], "2024-10-10"
            )

        with self.subTest("icontains"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "datum__icontains__2024"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["verbruiksobject"]["datum"], "2024-10-10"
            )

        with self.subTest("in"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "datum__in__2024-10-10|2025-10-10"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 2)

        with self.subTest("gt"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "datum__gt__2024-12-10"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["verbruiksobject"]["datum"], "2025-10-10"
            )

        with self.subTest("gte"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "datum__gte__2025-10-10"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["verbruiksobject"]["datum"], "2025-10-10"
            )

        with self.subTest("lt"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "datum__lt__2024-12-10"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["verbruiksobject"]["datum"], "2024-10-10"
            )

        with self.subTest("lte"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "datum__lte__2024-10-10"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["verbruiksobject"]["datum"], "2024-10-10"
            )

    def test_verbruiksobject_attr_filter_with_comma(self):
        filter = "naam__icontains__test,naam__icontains__abc"

        response = self.client.get(
            self.path,
            {"verbruiksobject_attr": filter},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            [
                ErrorDetail(
                    string=_(
                        "Filter '{}' moet de format 'key__operator__value' hebben, "
                        "komma's kunnen alleen in de `waarde` worden toegevoegd"
                    ).format(filter),
                    code="invalid-data-attr-query",
                )
            ],
        )

    def test_verbruiksobject_attr_filter_with_wrong_shape(self):
        filter = "naam__icontains"

        response = self.client.get(
            self.path,
            {"verbruiksobject_attr": filter},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            [
                ErrorDetail(
                    string=_(
                        "Filter '{}' heeft niet de format 'key__operator__waarde'"
                    ).format(filter),
                    code="invalid-data-attr-query",
                )
            ],
        )

    def test_verbruiksobject_attr_filter_with_unknown_operator(self):

        response = self.client.get(
            self.path,
            {"verbruiksobject_attr": "naam__contains__test"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            [
                ErrorDetail(
                    string=_("operator `{}` is niet bekend/ondersteund").format(
                        "contains"
                    ),
                    code="invalid-data-attr-query",
                )
            ],
        )

    def test_verbruiksobject_attr_multiple_filters(self):
        schema = {
            "type": "object",
            "properties": {"naam": {"type": "string"}, "type": "string"},
            "required": ["naam"],
        }

        ProductFactory(
            product_type=ProductTypeFactory.create(
                verbruiksobject_schema=JsonSchemaFactory(schema=schema)
            ),
            verbruiksobject={"naam": "test", "type": "test"},
        )

        ProductFactory(
            product_type=ProductTypeFactory.create(
                verbruiksobject_schema=JsonSchemaFactory(schema=schema)
            ),
            verbruiksobject={"naam": "abc", "type": "abc"},
        )

        response = self.client.get(
            self.path,
            {"verbruiksobject_attr": ("naam__exact__test", "type__exact__test")},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["verbruiksobject"]["naam"], "test")
