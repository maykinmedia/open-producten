# from unittest.mock import Mock, patch
#
# from django.contrib.gis.geos import Point
import datetime

from django.urls import reverse

from freezegun import freeze_time
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient

# from open_producten.locaties.tests.factories import (
#     ContactFactory,
#     LocatieFactory,
#     OrganisatieFactory,
# )
from open_producten.producttypen.models import Link, ProductType
from open_producten.producttypen.tests.factories import (
    BestandFactory,
    LinkFactory,
    OnderwerpFactory,
    PrijsFactory,
    PrijsOptieFactory,
    ProductTypeFactory,
    UniformeProductNaamFactory,
    VraagFactory,
)
from open_producten.utils.tests.cases import BaseApiTestCase


class TestProducttypeViewSet(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        upn = UniformeProductNaamFactory.create()
        self.onderwerp = OnderwerpFactory()

        self.data = {
            "naam": "test-product-type",
            "samenvatting": "test",
            "beschrijving": "test test",
            "uniforme_product_naam": upn.uri,
            "onderwerp_ids": [self.onderwerp.id],
        }
        # self.product_type = ProductTypeFactory.create()
        # self.product_type.onderwerpen.add(self.onderwerp)
        # self.product_type.save()

        self.path = reverse("producttype-list")

    def detail_path(self, product_type):
        return reverse("producttype-detail", args=[product_type.id])

    def test_read_product_type_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_required_fields(self):
        response = self.client.post(self.path, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "uniforme_product_naam": [
                    ErrorDetail(string="Dit veld is vereist.", code="required")
                ],
                "naam": [ErrorDetail(string="Dit veld is vereist.", code="required")],
                "onderwerp_ids": [
                    ErrorDetail(string="Dit veld is vereist.", code="required")
                ],
                "beschrijving": [
                    ErrorDetail(string="Dit veld is vereist.", code="required")
                ],
            },
        )

    def test_create_minimal_product_type(self):
        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductType.objects.count(), 1)

        product_type = ProductType.objects.get(id=response.data["id"])
        onderwerp = product_type.onderwerpen.first()
        expected_data = {
            "id": str(product_type.id),
            "naam": product_type.naam,
            "samenvatting": product_type.samenvatting,
            "beschrijving": product_type.beschrijving,
            "uniforme_product_naam": product_type.uniforme_product_naam.uri,
            "vragen": [],
            "prijzen": [],
            "links": [],
            "bestanden": [],
            "gepubliceerd": False,
            "aanmaak_datum": product_type.aanmaak_datum.astimezone().isoformat(),
            "update_datum": product_type.update_datum.astimezone().isoformat(),
            "keywords": [],
            "onderwerpen": [
                {
                    "id": str(onderwerp.id),
                    "naam": onderwerp.naam,
                    "gepubliceerd": True,
                    "aanmaak_datum": onderwerp.aanmaak_datum.astimezone().isoformat(),
                    "update_datum": onderwerp.update_datum.astimezone().isoformat(),
                    "beschrijving": onderwerp.beschrijving,
                    "hoofd_onderwerp": onderwerp.hoofd_onderwerp,
                }
            ],
        }
        self.assertEqual(response.data, expected_data)

    def test_create_product_type_without_fields_returns_error(self):
        data = self.data.copy()
        data["onderwerp_ids"] = []
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
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
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
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
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
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
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
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

        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "onderwerp_ids": [
                    ErrorDetail(
                        string=f"Dubbel id: {onderwerp.id} op index 1.",
                        code="invalid",
                    )
                ],
            },
        )

    def test_update_minimal_product_type(self):
        product_type = ProductTypeFactory.create()
        response = self.client.put(self.detail_path(product_type), self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProductType.objects.count(), 1)

    def test_update_product_type_with_onderwerp(self):
        product_type = ProductTypeFactory.create()
        onderwerp = OnderwerpFactory.create()

        data = self.data | {"onderwerp_ids": [onderwerp.id]}
        response = self.client.put(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("onderwerpen__naam", flat=True)),
            [onderwerp.naam],
        )

    def test_update_product_type_removing_onderwerp(self):
        product_type = ProductTypeFactory.create()
        data = self.data | {"onderwerp_ids": []}
        response = self.client.put(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
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
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
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
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
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
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
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

        response = self.client.put(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "onderwerp_ids": [
                    ErrorDetail(
                        string=f"Dubbel id: {onderwerp.id} op index 1.",
                        code="invalid",
                    )
                ],
            },
        )

    def test_partial_update_product_type(self):
        product_type = ProductTypeFactory.create()

        # TODO add location_ids

        data = {"naam": "update"}

        response = self.client.patch(self.detail_path(product_type), data)
        product_type.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(product_type.naam, "update")

    def test_partial_update_product_type_with_duplicate_ids_returns_error(self):
        product_type = ProductTypeFactory.create()
        onderwerp = OnderwerpFactory.create()

        data = {
            "onderwerp_ids": [onderwerp.id, onderwerp.id],
        }

        response = self.client.patch(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "onderwerp_ids": [
                    ErrorDetail(
                        string=f"Dubbel id: {onderwerp.id} op index 1.",
                        code="invalid",
                    )
                ],
            },
        )

    def test_partial_update_product_type_removing_onderwerp(self):
        product_type = ProductTypeFactory.create()
        data = {"onderwerp_ids": []}
        response = self.client.patch(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
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

    def test_read_product_type_link(self):
        product_type = ProductTypeFactory.create()
        link = LinkFactory.create(product_type=product_type)

        response = self.client.get(self.detail_path(product_type))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = [
            {
                "id": str(link.id),
                "naam": link.naam,
                "url": link.url,
            }
        ]

        self.assertEqual(response.data["links"], expected_data)

    def test_read_product_type_vraag(self):
        product_type = ProductTypeFactory.create()
        vraag = VraagFactory.create(product_type=product_type)

        response = self.client.get(self.detail_path(product_type))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = [
            {
                "id": str(vraag.id),
                "vraag": vraag.vraag,
                "antwoord": vraag.antwoord,
            }
        ]

        self.assertEqual(response.data["vragen"], expected_data)

    def test_read_product_type_bestand(self):
        product_type = ProductTypeFactory.create()
        bestand = BestandFactory.create(product_type=product_type)

        response = self.client.get(self.detail_path(product_type))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = [
            {
                "id": str(bestand.id),
                "bestand": "http://testserver" + bestand.bestand.url,
            }
        ]
        self.assertEqual(response.data["bestanden"], expected_data)

    def test_read_product_type_prijs(self):
        product_type = ProductTypeFactory.create()
        prijs = PrijsFactory.create(product_type=product_type)
        prijs_optie = PrijsOptieFactory.create(prijs=prijs)

        response = self.client.get(self.detail_path(product_type))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = [
            {
                "id": str(prijs.id),
                "actief_vanaf": str(prijs.actief_vanaf),
                "prijsopties": [
                    {
                        "id": str(prijs_optie.id),
                        "bedrag": str(prijs_optie.bedrag),
                        "beschrijving": prijs_optie.beschrijving,
                    }
                ],
            }
        ]
        self.assertEqual(response.data["prijzen"], expected_data)

    def test_read_product_typen(self):
        product_type1 = ProductTypeFactory.create()
        product_type1.onderwerpen.add(self.onderwerp)
        product_type1.save()

        product_type2 = ProductTypeFactory.create()
        product_type2.onderwerpen.add(self.onderwerp)
        product_type2.save()

        response = self.client.get(self.path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        expected_data = [
            {
                "id": str(product_type1.id),
                "naam": product_type1.naam,
                "samenvatting": product_type1.samenvatting,
                "beschrijving": product_type1.beschrijving,
                "uniforme_product_naam": product_type1.uniforme_product_naam.uri,
                "vragen": [],
                "prijzen": [],
                "links": [],
                "bestanden": [],
                "gepubliceerd": True,
                "aanmaak_datum": product_type1.aanmaak_datum.astimezone().isoformat(),
                "update_datum": product_type1.update_datum.astimezone().isoformat(),
                "keywords": [],
                "onderwerpen": [
                    {
                        "id": str(self.onderwerp.id),
                        "naam": self.onderwerp.naam,
                        "gepubliceerd": True,
                        "aanmaak_datum": self.onderwerp.aanmaak_datum.astimezone().isoformat(),
                        "update_datum": self.onderwerp.update_datum.astimezone().isoformat(),
                        "beschrijving": self.onderwerp.beschrijving,
                        "hoofd_onderwerp": self.onderwerp.hoofd_onderwerp,
                    }
                ],
            },
            {
                "id": str(product_type2.id),
                "naam": product_type2.naam,
                "samenvatting": product_type2.samenvatting,
                "beschrijving": product_type2.beschrijving,
                "uniforme_product_naam": product_type2.uniforme_product_naam.uri,
                "vragen": [],
                "prijzen": [],
                "links": [],
                "bestanden": [],
                "gepubliceerd": True,
                "aanmaak_datum": product_type2.aanmaak_datum.astimezone().isoformat(),
                "update_datum": product_type2.update_datum.astimezone().isoformat(),
                "keywords": [],
                "onderwerpen": [
                    {
                        "id": str(self.onderwerp.id),
                        "naam": self.onderwerp.naam,
                        "gepubliceerd": True,
                        "aanmaak_datum": self.onderwerp.aanmaak_datum.astimezone().isoformat(),
                        "update_datum": self.onderwerp.update_datum.astimezone().isoformat(),
                        "beschrijving": self.onderwerp.beschrijving,
                        "hoofd_onderwerp": self.onderwerp.hoofd_onderwerp,
                    }
                ],
            },
        ]
        self.assertCountEqual(response.data["results"], expected_data)

    def test_read_product_type(self):
        product_type = ProductTypeFactory.create()
        product_type.onderwerpen.add(self.onderwerp)
        product_type.save()

        response = self.client.get(self.detail_path(product_type))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {
            "id": str(product_type.id),
            "naam": product_type.naam,
            "samenvatting": product_type.samenvatting,
            "beschrijving": product_type.beschrijving,
            "uniforme_product_naam": product_type.uniforme_product_naam.uri,
            "vragen": [],
            "prijzen": [],
            "links": [],
            "bestanden": [],
            "gepubliceerd": True,
            "aanmaak_datum": product_type.aanmaak_datum.astimezone().isoformat(),
            "update_datum": product_type.update_datum.astimezone().isoformat(),
            "keywords": [],
            "onderwerpen": [
                {
                    "id": str(self.onderwerp.id),
                    "naam": self.onderwerp.naam,
                    "gepubliceerd": True,
                    "aanmaak_datum": self.onderwerp.aanmaak_datum.astimezone().isoformat(),
                    "update_datum": self.onderwerp.update_datum.astimezone().isoformat(),
                    "beschrijving": self.onderwerp.beschrijving,
                    "hoofd_onderwerp": self.onderwerp.hoofd_onderwerp,
                }
            ],
        }

        self.assertEqual(response.data, expected_data)

    def test_delete_product_type(self):
        product_type = ProductTypeFactory.create()

        LinkFactory.create(product_type=product_type)

        response = self.client.delete(self.detail_path(product_type))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ProductType.objects.count(), 0)
        self.assertEqual(Link.objects.count(), 0)


@freeze_time("2024-01-01")
class TestProductTypeActions(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        self.product_type = ProductTypeFactory.create()
        self.list_path = reverse("producttype-actuele-prijzen")
        self.detail_path = reverse(
            "producttype-actuele-prijs", args=(self.product_type.id,)
        )

        self.expected_data = {
            "id": str(self.product_type.id),
            "naam": self.product_type.naam,
            "upl_naam": self.product_type.uniforme_product_naam.naam,
            "upl_uri": self.product_type.uniforme_product_naam.uri,
            "actuele_prijs": None,
        }

    def test_get_actuele_prijzen_when_product_type_has_no_prijzen(self):
        response = self.client.get(self.list_path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            [
                self.expected_data,
            ],
        )

    def test_get_actuele_prijs_when_product_type_has_no_prijzen(self):
        response = self.client.get(self.detail_path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            self.expected_data,
        )

    def test_get_actuele_prijzen_when_product_type_only_has_prijs_in_future(self):
        PrijsFactory.create(
            product_type=self.product_type, actief_vanaf=datetime.date(2024, 2, 2)
        )

        response = self.client.get(self.list_path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            [
                self.expected_data,
            ],
        )

    def test_get_actuele_prijzen_when_product_type_has_actuele_prijs(self):
        prijs = PrijsFactory.create(
            product_type=self.product_type,
            actief_vanaf=datetime.date(2024, 1, 1),
        )

        optie = PrijsOptieFactory.create(prijs=prijs)

        response = self.client.get(self.list_path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            [
                self.expected_data
                | {
                    "actuele_prijs": {
                        "id": str(prijs.id),
                        "product_type_id": self.product_type.id,
                        "actief_vanaf": "2024-01-01",
                        "prijsopties": [
                            {
                                "bedrag": str(optie.bedrag),
                                "beschrijving": optie.beschrijving,
                                "id": str(optie.id),
                            }
                        ],
                    },
                },
            ],
        )

    def test_get_actuele_prijs_when_product_type_has_actuele_prijs(self):
        prijs = PrijsFactory.create(
            product_type=self.product_type,
            actief_vanaf=datetime.date(2024, 1, 1),
        )

        optie = PrijsOptieFactory.create(prijs=prijs)

        response = self.client.get(self.detail_path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            self.expected_data
            | {
                "actuele_prijs": {
                    "id": str(prijs.id),
                    "product_type_id": self.product_type.id,
                    "actief_vanaf": "2024-01-01",
                    "prijsopties": [
                        {
                            "bedrag": str(optie.bedrag),
                            "beschrijving": optie.beschrijving,
                            "id": str(optie.id),
                        }
                    ],
                },
            },
        )
