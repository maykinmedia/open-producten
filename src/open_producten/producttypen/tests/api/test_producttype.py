# from unittest.mock import Mock, patch
#
# from django.contrib.gis.geos import Point
from django.forms import model_to_dict

from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient

# from open_producten.locaties.tests.factories import (
#     ContactFactory,
#     LocatieFactory,
#     OrganisatieFactory,
# )
from open_producten.producttypen.models import Link, ProductType
from open_producten.producttypen.tests.factories import (
    LinkFactory,
    OnderwerpFactory,
    ProductTypeFactory,
    UniformeProductNaamFactory,
)
from open_producten.utils.tests.cases import BaseApiTestCase
from open_producten.utils.tests.helpers import model_to_dict_with_id


def product_type_to_dict(product_type):
    product_type_dict = model_to_dict_with_id(product_type)
    product_type_dict["vragen"] = [
        model_to_dict(vraag) for vraag in product_type.vragen.all()
    ]
    product_type_dict["prijzen"] = [
        model_to_dict(prijs) for prijs in product_type.prijzen.all()
    ]
    product_type_dict["links"] = [
        model_to_dict(link) for link in product_type.links.all()
    ]
    product_type_dict["bestanden"] = [
        model_to_dict(bestand) for bestand in product_type.bestanden.all()
    ]

    product_type_dict["onderwerpen"] = []
    for onderwerp in product_type.onderwerpen.all():
        onderwerp_dict = model_to_dict_with_id(
            onderwerp, exclude=("path", "depth", "numchild")
        )
        onderwerp_dict["aanmaak_datum"] = str(
            onderwerp.aanmaak_datum.astimezone().isoformat()
        )
        onderwerp_dict["update_datum"] = str(
            onderwerp.update_datum.astimezone().isoformat()
        )
        product_type_dict["onderwerpen"].append(onderwerp_dict)

    product_type_dict["aanmaak_datum"] = str(
        product_type.aanmaak_datum.astimezone().isoformat()
    )
    product_type_dict["update_datum"] = str(
        product_type.update_datum.astimezone().isoformat()
    )
    product_type_dict["uniforme_product_naam"] = product_type.uniforme_product_naam.uri
    return product_type_dict


class TestProducttypeViewSet(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        upn = UniformeProductNaamFactory.create()
        onderwerp = OnderwerpFactory()

        self.data = {
            "naam": "test-product-type",
            "samenvatting": "test",
            "beschrijving": "test test",
            "uniforme_product_naam": upn.uri,
            "onderwerp_ids": [onderwerp.id],
        }

        self.path = "/api/v1/producttypen/"

    def test_read_product_type_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, 401)

    def test_create_minimal_product_type(self):
        response = self.post(self.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ProductType.objects.count(), 1)
        product_type = ProductType.objects.first()
        self.assertEqual(response.data, product_type_to_dict(product_type))

    def test_create_product_type_without_fields_returns_error(self):
        data = self.data.copy()
        data["onderwerp_ids"] = []
        response = self.post(data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "onderwerp_ids": [
                    ErrorDetail(
                        string="Er is minimaal één onderwerp vereist.", code="invalid"
                    )
                ]
            },
        )

    def test_create_product_type_with_onderwerp(self):
        onderwerp = OnderwerpFactory.create()

        data = self.data | {"onderwerp_ids": [onderwerp.id]}
        response = self.post(data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("onderwerpen__naam", flat=True)),
            [onderwerp.naam],
        )

    # @patch(
    #     "open_producten.locaties.models.locatie.geocode_address",
    #     new=Mock(return_value=Point((4.84303667, 52.38559043))),
    # )
    # def test_create_product_type_with_location(self):
    #     locatie = LocatieFactory.create()
    #
    #     data = self.data | {"locatie_ids": [locatie.id]}
    #     response = self.post(data)
    #
    #     self.assertEqual(response.status_code, 201)
    #     self.assertEqual(ProductType.objects.count(), 1)
    #     self.assertEqual(
    #         list(ProductType.objects.values_list("locaties__naam", flat=True)),
    #         [locatie.naam],
    #     )
    #
    # @patch(
    #     "open_producten.locaties.models.locatie.geocode_address",
    #     new=Mock(return_value=Point((4.84303667, 52.38559043))),
    # )
    # def test_create_product_type_with_organisation(self):
    #     organisatie = OrganisatieFactory.create()
    #
    #     data = self.data | {"organisatie_ids": [organisatie.id]}
    #     response = self.post(data)
    #
    #     self.assertEqual(response.status_code, 201)
    #     self.assertEqual(ProductType.objects.count(), 1)
    #     self.assertEqual(
    #         list(ProductType.objects.values_list("organisaties__naam", flat=True)),
    #         [organisatie.naam],
    #     )
    #
    # @patch(
    #     "open_producten.locaties.models.locatie.geocode_address",
    #     new=Mock(return_value=Point((4.84303667, 52.38559043))),
    # )
    # def test_create_product_type_with_contact(self):
    #     contact = ContactFactory.create()
    #
    #     data = self.data | {"contact_ids": [contact.id]}
    #     response = self.post(data)
    #
    #     self.assertEqual(response.status_code, 201)
    #     self.assertEqual(ProductType.objects.count(), 1)
    #     self.assertEqual(
    #         list(ProductType.objects.values_list("contacten__voornaam", flat=True)),
    #         [contact.voornaam],
    #     )
    #
    #     # contact org is added in ProductType clean
    #     self.assertEqual(ProductType.objects.first().organisations.count(), 1)

    def test_create_product_type_with_duplicate_ids_returns_error(self):
        onderwerp = OnderwerpFactory.create()

        # TODO add location_ids

        data = self.data | {
            "onderwerp_ids": [onderwerp.id, onderwerp.id],
        }

        response = self.post(data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "onderwerp_ids": [
                    ErrorDetail(
                        string=f"Dubbel Onderwerp id: {onderwerp.id} op index 1.",
                        code="invalid",
                    )
                ],
            },
        )

    def test_update_minimal_product_type(self):
        product_type = ProductTypeFactory.create()

        response = self.put(product_type.id, self.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ProductType.objects.count(), 1)

    def test_update_product_type_with_onderwerp(self):
        product_type = ProductTypeFactory.create()
        onderwerp = OnderwerpFactory.create()

        data = self.data | {"onderwerp_ids": [onderwerp.id]}
        response = self.put(product_type.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("onderwerpen__naam", flat=True)),
            [onderwerp.naam],
        )

    # @patch(
    #     "open_producten.locaties.models.locatie.geocode_address",
    #     new=Mock(return_value=Point((4.84303667, 52.38559043))),
    # )
    # def test_update_product_type_with_location(self):
    #     product_type = ProductTypeFactory.create()
    #     locatie = LocatieFactory.create()
    #
    #     data = self.data | {"locatie_ids": [locatie.id]}
    #     response = self.put(product_type.id, data)
    #
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(ProductType.objects.count(), 1)
    #     self.assertEqual(
    #         list(ProductType.objects.values_list("locaties__naam", flat=True)),
    #         [locatie.naam],
    #     )
    #
    # @patch(
    #     "open_producten.locaties.models.locatie.geocode_address",
    #     new=Mock(return_value=Point((4.84303667, 52.38559043))),
    # )
    # def test_update_product_type_with_organisation(self):
    #     product_type = ProductTypeFactory.create()
    #     organisatie = OrganisatieFactory.create()
    #
    #     data = self.data | {"organisation_ids": [organisatie.id]}
    #     response = self.put(product_type.id, data)
    #
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(ProductType.objects.count(), 1)
    #     self.assertEqual(
    #         list(ProductType.objects.values_list("organisaties__naam", flat=True)),
    #         [organisatie.naam],
    #     )
    #
    # @patch(
    #     "open_producten.locaties.models.locatie.geocode_address",
    #     new=Mock(return_value=Point((4.84303667, 52.38559043))),
    # )
    # def test_update_product_type_with_contact(self):
    #     product_type = ProductTypeFactory.create()
    #     contact = ContactFactory.create()
    #
    #     data = self.data | {"contact_ids": [contact.id]}
    #     response = self.put(product_type.id, data)
    #
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(ProductType.objects.count(), 1)
    #     self.assertEqual(
    #         list(ProductType.objects.values_list("contacten__voornaam", flat=True)),
    #         [contact.voornaam],
    #     )
    #
    #     # contact org is added in ProductType clean
    #     self.assertEqual(ProductType.objects.first().organisations.count(), 1)

    def test_update_product_type_with_duplicate_ids_returns_error(self):
        product_type = ProductTypeFactory.create()
        onderwerp = OnderwerpFactory.create()

        # TODO add location_ids

        data = self.data | {
            "onderwerp_ids": [onderwerp.id, onderwerp.id],
        }

        response = self.put(product_type.id, data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "onderwerp_ids": [
                    ErrorDetail(
                        string=f"Dubbel Onderwerp id: {onderwerp.id} op index 1.",
                        code="invalid",
                    )
                ],
            },
        )

    def test_partial_update_product_type(self):
        product_type = ProductTypeFactory.create()

        # TODO add location_ids

        product_type.save()

        data = {"naam": "update"}

        response = self.patch(product_type.id, data)
        product_type.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(product_type.naam, "update")

    def test_partial_update_product_type_with_duplicate_ids_returns_error(self):
        product_type = ProductTypeFactory.create()
        onderwerp = OnderwerpFactory.create()

        data = {
            "onderwerp_ids": [onderwerp.id, onderwerp.id],
        }

        response = self.patch(product_type.id, data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "onderwerp_ids": [
                    ErrorDetail(
                        string=f"Dubbel Onderwerp id: {onderwerp.id} op index 1.",
                        code="invalid",
                    )
                ],
            },
        )

    def test_read_product_typen(self):
        product_type = ProductTypeFactory.create()

        response = self.get()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"], [product_type_to_dict(product_type)])

    def test_read_product_type(self):
        product_type = ProductTypeFactory.create()

        response = self.get(product_type.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, product_type_to_dict(product_type))

    def test_delete_product_type(self):
        product_type = ProductTypeFactory.create()
        product_type.save()
        LinkFactory.create(product_type=product_type)

        response = self.delete(product_type.id)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(ProductType.objects.count(), 0)
        self.assertEqual(Link.objects.count(), 0)
