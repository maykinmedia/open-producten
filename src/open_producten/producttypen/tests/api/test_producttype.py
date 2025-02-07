import datetime

from django.urls import reverse
from django.utils.translation import gettext as _

from freezegun import freeze_time
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient

from open_producten.locaties.tests.factories import (
    ContactFactory,
    LocatieFactory,
    OrganisatieFactory,
)
from open_producten.producttypen.models import (
    Eigenschap,
    ExterneCode,
    Link,
    ProductType,
)
from open_producten.producttypen.tests.factories import (
    BestandFactory,
    EigenschapFactory,
    ExterneCodeFactory,
    LinkFactory,
    PrijsFactory,
    PrijsOptieFactory,
    ProductTypeFactory,
    ThemaFactory,
    UniformeProductNaamFactory,
    VraagFactory,
)
from open_producten.utils.tests.cases import BaseApiTestCase


class TestProducttypeViewSet(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        upn = UniformeProductNaamFactory.create()
        self.thema = ThemaFactory()

        self.data = {
            "naam": "test-product-type",
            "code": "PT=12345",
            "samenvatting": "test",
            "beschrijving": "test test",
            "uniforme_product_naam": upn.naam,
            "thema_ids": [self.thema.id],
        }

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
                    ErrorDetail(string=_("This field is required."), code="required")
                ],
                "naam": [
                    ErrorDetail(string=_("This field is required."), code="required")
                ],
                "thema_ids": [
                    ErrorDetail(string=_("This field is required."), code="required")
                ],
                "beschrijving": [
                    ErrorDetail(string=_("This field is required."), code="required")
                ],
                "code": [
                    ErrorDetail(string=_("This field is required."), code="required")
                ],
            },
        )

    def test_create_minimal_product_type(self):
        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductType.objects.count(), 1)

        product_type = ProductType.objects.first()
        thema = product_type.themas.first()
        expected_data = {
            "id": str(product_type.id),
            "naam": product_type.naam,
            "code": product_type.code,
            "samenvatting": product_type.samenvatting,
            "beschrijving": product_type.beschrijving,
            "uniforme_product_naam": product_type.uniforme_product_naam.naam,
            "toegestane_statussen": [],
            "vragen": [],
            "prijzen": [],
            "links": [],
            "bestanden": [],
            "locaties": [],
            "organisaties": [],
            "contacten": [],
            "eigenschappen": [],
            "externe_codes": [],
            "gepubliceerd": False,
            "aanmaak_datum": product_type.aanmaak_datum.astimezone().isoformat(),
            "update_datum": product_type.update_datum.astimezone().isoformat(),
            "keywords": [],
            "themas": [
                {
                    "id": str(thema.id),
                    "naam": thema.naam,
                    "gepubliceerd": True,
                    "aanmaak_datum": thema.aanmaak_datum.astimezone().isoformat(),
                    "update_datum": thema.update_datum.astimezone().isoformat(),
                    "beschrijving": thema.beschrijving,
                    "hoofd_thema": thema.hoofd_thema,
                }
            ],
        }
        self.assertEqual(response.data, expected_data)

    def test_create_product_type_without_thema_returns_error(self):
        data = self.data.copy()
        data["thema_ids"] = []
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "thema_ids": [
                    ErrorDetail(
                        string=_("Er is minimaal één thema vereist."), code="invalid"
                    )
                ],
            },
        )

    def test_create_product_type_with_location(self):
        locatie = LocatieFactory.create()

        data = self.data | {"locatie_ids": [locatie.id]}
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("locaties__naam", flat=True)),
            [locatie.naam],
        )

    def test_create_product_type_with_organisatie(self):
        organisatie = OrganisatieFactory.create()

        data = self.data | {"organisatie_ids": [organisatie.id]}
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("organisaties__naam", flat=True)),
            [organisatie.naam],
        )

    def test_create_product_type_with_contact(self):
        contact = ContactFactory.create()

        data = self.data | {"contact_ids": [contact.id]}
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("contacten__voornaam", flat=True)),
            [contact.voornaam],
        )

        # contact org is added in ProductType clean
        self.assertEqual(ProductType.objects.first().organisaties.count(), 1)

    def test_create_product_type_with_toegestane_statussen(self):
        response = self.client.post(
            self.path, self.data | {"toegestane_statussen": ["gereed"]}
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(response.data["toegestane_statussen"], ["gereed"])

    def test_create_product_type_with_duplicate_eigenschap_naams_returns_error(self):
        data = self.data | {
            "eigenschappen": [
                {"naam": "doelgroep", "waarde": "inwoners"},
                {"naam": "doelgroep", "waarde": "inwoners"},
            ],
        }
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "eigenschappen": [
                    ErrorDetail(
                        string=_(
                            "De eigenschappen van een product type moeten een unieke naam hebben."
                        ),
                        code="invalid",
                    )
                ],
            },
        )

    def test_create_product_type_with_duplicate_externe_code_systemen_returns_error(
        self,
    ):
        data = self.data | {
            "externe_codes": [
                {"naam": "ISO", "code": "123"},
                {"naam": "ISO", "code": "123"},
            ],
        }
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "externe_codes": [
                    ErrorDetail(
                        string=_(
                            "De externe codes van een product type moeten een unieke naam hebben."
                        ),
                        code="invalid",
                    )
                ],
            },
        )

    def test_create_product_type_with_duplicate_ids_returns_error(self):
        thema = ThemaFactory.create()

        locatie = LocatieFactory.create()

        data = self.data | {
            "thema_ids": [thema.id, thema.id],
            "locatie_ids": [locatie.id, locatie.id],
        }

        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "thema_ids": [
                    ErrorDetail(
                        string=_("Dubbel id: {} op index 1.").format(thema.id),
                        code="invalid",
                    )
                ],
                "locatie_ids": [
                    ErrorDetail(
                        string=_("Dubbel id: {} op index 1.").format(locatie.id),
                        code="invalid",
                    )
                ],
            },
        )

    def test_create_complete_product_type(self):
        locatie = LocatieFactory.create()
        organisatie = OrganisatieFactory.create()
        contact = ContactFactory.create()

        data = self.data | {
            "locatie_ids": [locatie.id],
            "organisatie_ids": [organisatie.id],
            "contact_ids": [contact.id],
            "eigenschappen": [{"naam": "doelgroep", "waarde": "inwoner"}],
            "externe_codes": [{"naam": "ISO", "code": "123"}],
        }
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductType.objects.count(), 1)

        product_type = ProductType.objects.first()
        thema = product_type.themas.first()

        expected_data = {
            "id": str(product_type.id),
            "naam": product_type.naam,
            "code": product_type.code,
            "samenvatting": product_type.samenvatting,
            "beschrijving": product_type.beschrijving,
            "uniforme_product_naam": product_type.uniforme_product_naam.naam,
            "toegestane_statussen": [],
            "vragen": [],
            "prijzen": [],
            "links": [],
            "bestanden": [],
            "locaties": [
                {
                    "id": str(locatie.id),
                    "naam": locatie.naam,
                    "email": locatie.email,
                    "telefoonnummer": locatie.telefoonnummer,
                    "straat": locatie.straat,
                    "huisnummer": locatie.huisnummer,
                    "postcode": locatie.postcode,
                    "stad": locatie.stad,
                }
            ],
            "organisaties": [
                {
                    "id": str(organisatie.id),
                    "code": str(organisatie.code),
                    "naam": organisatie.naam,
                    "email": organisatie.email,
                    "telefoonnummer": organisatie.telefoonnummer,
                    "straat": organisatie.straat,
                    "huisnummer": organisatie.huisnummer,
                    "postcode": organisatie.postcode,
                    "stad": organisatie.stad,
                },
                {
                    "id": str(contact.organisatie.id),
                    "code": str(contact.organisatie.code),
                    "naam": contact.organisatie.naam,
                    "email": contact.organisatie.email,
                    "telefoonnummer": contact.organisatie.telefoonnummer,
                    "straat": contact.organisatie.straat,
                    "huisnummer": contact.organisatie.huisnummer,
                    "postcode": contact.organisatie.postcode,
                    "stad": contact.organisatie.stad,
                },
            ],
            "contacten": [
                {
                    "id": str(contact.id),
                    "voornaam": contact.voornaam,
                    "achternaam": contact.achternaam,
                    "email": contact.email,
                    "telefoonnummer": contact.telefoonnummer,
                    "rol": contact.rol,
                    "organisatie": {
                        "id": str(contact.organisatie.id),
                        "code": str(contact.organisatie.code),
                        "naam": contact.organisatie.naam,
                        "email": contact.organisatie.email,
                        "telefoonnummer": contact.organisatie.telefoonnummer,
                        "straat": contact.organisatie.straat,
                        "huisnummer": contact.organisatie.huisnummer,
                        "postcode": contact.organisatie.postcode,
                        "stad": contact.organisatie.stad,
                    },
                }
            ],
            "eigenschappen": [{"naam": "doelgroep", "waarde": "inwoner"}],
            "externe_codes": [{"naam": "ISO", "code": "123"}],
            "gepubliceerd": False,
            "aanmaak_datum": product_type.aanmaak_datum.astimezone().isoformat(),
            "update_datum": product_type.update_datum.astimezone().isoformat(),
            "keywords": [],
            "themas": [
                {
                    "id": str(thema.id),
                    "naam": thema.naam,
                    "gepubliceerd": True,
                    "aanmaak_datum": thema.aanmaak_datum.astimezone().isoformat(),
                    "update_datum": thema.update_datum.astimezone().isoformat(),
                    "beschrijving": thema.beschrijving,
                    "hoofd_thema": thema.hoofd_thema,
                }
            ],
        }
        self.assertEqual(response.data, expected_data)

    def test_update_minimal_product_type(self):
        product_type = ProductTypeFactory.create()
        response = self.client.put(self.detail_path(product_type), self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProductType.objects.count(), 1)

    def test_update_product_type_with_thema(self):
        product_type = ProductTypeFactory.create()
        thema = ThemaFactory.create()

        data = self.data | {"thema_ids": [thema.id]}
        response = self.client.put(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("themas__naam", flat=True)),
            [thema.naam],
        )

    def test_update_product_type_removing_thema(self):
        product_type = ProductTypeFactory.create()
        data = self.data | {"thema_ids": []}
        response = self.client.put(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "thema_ids": [
                    ErrorDetail(
                        string=_("Er is minimaal één thema vereist."), code="invalid"
                    )
                ]
            },
        )

    def test_update_product_type_with_location(self):
        product_type = ProductTypeFactory.create()
        locatie = LocatieFactory.create()

        data = self.data | {"locatie_ids": [locatie.id]}
        response = self.client.put(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("locaties__naam", flat=True)),
            [locatie.naam],
        )

    def test_update_product_type_with_organisatie(self):
        product_type = ProductTypeFactory.create()
        organisatie = OrganisatieFactory.create()

        data = self.data | {"organisatie_ids": [organisatie.id]}
        response = self.client.put(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("organisaties__naam", flat=True)),
            [organisatie.naam],
        )

    def test_update_product_type_with_contact(self):
        product_type = ProductTypeFactory.create()
        contact = ContactFactory.create()

        data = self.data | {"contact_ids": [contact.id]}
        response = self.client.put(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("contacten__voornaam", flat=True)),
            [contact.voornaam],
        )

        # contact org is added in ProductType clean
        self.assertEqual(ProductType.objects.first().organisaties.count(), 1)

    def test_update_product_type_with_duplicate_ids_returns_error(self):
        product_type = ProductTypeFactory.create()
        thema = ThemaFactory.create()
        locatie = LocatieFactory.create()

        data = self.data | {
            "thema_ids": [thema.id, thema.id],
            "locatie_ids": [locatie.id, locatie.id],
        }

        response = self.client.put(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "thema_ids": [
                    ErrorDetail(
                        string=_("Dubbel id: {} op index 1.").format(thema.id),
                        code="invalid",
                    )
                ],
                "locatie_ids": [
                    ErrorDetail(
                        string=_("Dubbel id: {} op index 1.").format(locatie.id),
                        code="invalid",
                    )
                ],
            },
        )

    def test_update_product_type_with_eigenschap(self):
        product_type = ProductTypeFactory.create()

        eigenschappen = [{"naam": "doelgroep", "waarde": "inwoners"}]
        data = self.data | {"eigenschappen": eigenschappen}
        response = self.client.put(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Eigenschap.objects.count(), 1)
        self.assertEqual(response.data["eigenschappen"], eigenschappen)

    def test_update_product_type_with_updating_exising_eigenschap(self):
        product_type = ProductTypeFactory.create()
        eigenschap = EigenschapFactory.create(product_type=product_type)

        eigenschappen = [{"naam": eigenschap.naam, "waarde": "inwoners"}]
        data = self.data | {"eigenschappen": eigenschappen}
        response = self.client.put(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Eigenschap.objects.count(), 1)
        self.assertEqual(Eigenschap.objects.first().id, eigenschap.id)
        self.assertEqual(response.data["eigenschappen"], eigenschappen)

    def test_update_product_type_removing_exising_eigenschappen_and_adding_new_ones(
        self,
    ):
        product_type = ProductTypeFactory.create()
        EigenschapFactory.create(product_type=product_type)
        EigenschapFactory.create(product_type=product_type)

        eigenschappen = [
            {"naam": "doelgroep", "waarde": "inwoners"},
            {"naam": "test", "waarde": "123"},
        ]
        data = self.data | {"eigenschappen": eigenschappen}
        response = self.client.put(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Eigenschap.objects.count(), 2)
        self.assertEqual(response.data["eigenschappen"], eigenschappen)

    def test_update_product_type_removing_eigenschappen(self):
        product_type = ProductTypeFactory.create()
        EigenschapFactory.create(product_type=product_type)
        EigenschapFactory.create(product_type=product_type)

        eigenschappen = []
        data = self.data | {"eigenschappen": eigenschappen}
        response = self.client.put(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Eigenschap.objects.count(), 0)
        self.assertEqual(response.data["eigenschappen"], eigenschappen)

    def test_update_product_type_with_externe_code(self):
        product_type = ProductTypeFactory.create()

        externe_codes = [{"naam": "ISO", "code": "123"}]
        data = self.data | {"externe_codes": externe_codes}
        response = self.client.put(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExterneCode.objects.count(), 1)
        self.assertEqual(response.data["externe_codes"], externe_codes)

    def test_update_product_type_with_updating_exising_externe_code(self):
        product_type = ProductTypeFactory.create()
        externe_code = ExterneCodeFactory.create(product_type=product_type)

        externe_codes = [{"naam": externe_code.naam, "code": "456"}]
        data = self.data | {"externe_codes": externe_codes}
        response = self.client.put(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExterneCode.objects.count(), 1)
        self.assertEqual(ExterneCode.objects.first().id, externe_code.id)
        self.assertEqual(response.data["externe_codes"], externe_codes)

    def test_update_product_type_removing_exising_externe_codes_and_adding_new_ones(
        self,
    ):
        product_type = ProductTypeFactory.create()
        ExterneCodeFactory.create(product_type=product_type)
        ExterneCodeFactory.create(product_type=product_type)

        externe_codes = [
            {"naam": "ISO", "code": "123"},
            {"naam": "CBS", "code": "1234"},
        ]
        data = self.data | {"externe_codes": externe_codes}
        response = self.client.put(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExterneCode.objects.count(), 2)
        self.assertEqual(response.data["externe_codes"], externe_codes)

    def test_update_product_type_removing_externe_codes(self):
        product_type = ProductTypeFactory.create()
        ExterneCodeFactory.create(product_type=product_type)
        ExterneCodeFactory.create(product_type=product_type)

        externe_codes = []
        data = self.data | {"externe_codes": externe_codes}
        response = self.client.put(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExterneCode.objects.count(), 0)
        self.assertEqual(response.data["externe_codes"], externe_codes)

    def test_partial_update_product_type(self):
        product_type = ProductTypeFactory.create()
        locatie = LocatieFactory.create()

        product_type.locaties.add(locatie)
        product_type.save()

        data = {"naam": "update"}

        response = self.client.patch(self.detail_path(product_type), data)
        product_type.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(product_type.locaties.count(), 1)
        self.assertEqual(product_type.naam, "update")

    def test_partial_update_product_type_with_duplicate_ids_returns_error(self):
        product_type = ProductTypeFactory.create()
        thema = ThemaFactory.create()

        data = {
            "thema_ids": [thema.id, thema.id],
        }

        response = self.client.patch(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "thema_ids": [
                    ErrorDetail(
                        string=_("Dubbel id: {} op index 1.").format(thema.id),
                        code="invalid",
                    )
                ],
            },
        )

    def test_partial_update_product_type_removing_thema(self):
        product_type = ProductTypeFactory.create()
        data = {"thema_ids": []}
        response = self.client.patch(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "thema_ids": [
                    ErrorDetail(
                        string=_("Er is minimaal één thema vereist."), code="invalid"
                    )
                ]
            },
        )

    def test_partial_update_eigenschappen_and_externe_codes_are_kept_when_naam_not_passed(
        self,
    ):
        product_type = ProductTypeFactory.create()
        EigenschapFactory.create(product_type=product_type)
        ExterneCodeFactory.create(product_type=product_type)
        data = {"naam": "update"}

        response = self.client.patch(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Eigenschap.objects.count(), 1)
        self.assertEqual(ExterneCode.objects.count(), 1)

    def test_partial_update_product_type_with_eigenschap(self):
        product_type = ProductTypeFactory.create()

        eigenschappen = [{"naam": "doelgroep", "waarde": "inwoners"}]
        data = {"eigenschappen": eigenschappen}
        response = self.client.patch(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Eigenschap.objects.count(), 1)
        self.assertEqual(response.data["eigenschappen"], eigenschappen)

    def test_partial_update_product_type_with_updating_exising_eigenschap(self):
        product_type = ProductTypeFactory.create()
        eigenschap = EigenschapFactory.create(product_type=product_type)

        eigenschappen = [{"naam": eigenschap.naam, "waarde": "inwoners"}]
        data = {"eigenschappen": eigenschappen}
        response = self.client.patch(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Eigenschap.objects.count(), 1)
        self.assertEqual(Eigenschap.objects.first().id, eigenschap.id)
        self.assertEqual(response.data["eigenschappen"], eigenschappen)

    def test_partial_update_product_type_removing_exising_eigenschappen_and_adding_new_ones(
        self,
    ):
        product_type = ProductTypeFactory.create()
        EigenschapFactory.create(product_type=product_type)
        EigenschapFactory.create(product_type=product_type)

        eigenschappen = [
            {"naam": "doelgroep", "waarde": "inwoners"},
            {"naam": "test", "waarde": "123"},
        ]
        data = {"eigenschappen": eigenschappen}
        response = self.client.patch(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Eigenschap.objects.count(), 2)
        self.assertEqual(response.data["eigenschappen"], eigenschappen)

    def test_partial_update_product_type_removing_eigenschappen(self):
        product_type = ProductTypeFactory.create()
        EigenschapFactory.create(product_type=product_type)
        EigenschapFactory.create(product_type=product_type)

        eigenschappen = []
        data = {"eigenschappen": eigenschappen}
        response = self.client.patch(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Eigenschap.objects.count(), 0)
        self.assertEqual(response.data["eigenschappen"], eigenschappen)

    def test_partial_update_product_type_with_externe_code(self):
        product_type = ProductTypeFactory.create()

        externe_codes = [{"naam": "ISO", "code": "123"}]
        data = {"externe_codes": externe_codes}
        response = self.client.patch(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExterneCode.objects.count(), 1)
        self.assertEqual(response.data["externe_codes"], externe_codes)

    def test_parial_update_product_type_with_updating_exising_externe_code(self):
        product_type = ProductTypeFactory.create()
        externe_code = ExterneCodeFactory.create(product_type=product_type)

        externe_codes = [{"naam": externe_code.naam, "code": "456"}]
        data = {"externe_codes": externe_codes}
        response = self.client.patch(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExterneCode.objects.count(), 1)
        self.assertEqual(ExterneCode.objects.first().id, externe_code.id)
        self.assertEqual(response.data["externe_codes"], externe_codes)

    def test_partial_update_product_type_removing_exising_externe_codes_and_adding_new_ones(
        self,
    ):
        product_type = ProductTypeFactory.create()
        ExterneCodeFactory.create(product_type=product_type)
        ExterneCodeFactory.create(product_type=product_type)

        externe_codes = [
            {"naam": "ISO", "code": "123"},
            {"naam": "CBS", "code": "1234"},
        ]
        data = {"externe_codes": externe_codes}
        response = self.client.patch(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExterneCode.objects.count(), 2)
        self.assertEqual(response.data["externe_codes"], externe_codes)

    def test_partial_update_product_type_removing_externe_codes(self):
        product_type = ProductTypeFactory.create()
        ExterneCodeFactory.create(product_type=product_type)
        ExterneCodeFactory.create(product_type=product_type)

        externe_codes = []
        data = {"externe_codes": externe_codes}
        response = self.client.patch(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExterneCode.objects.count(), 0)
        self.assertEqual(response.data["externe_codes"], externe_codes)

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
        product_type1.themas.add(self.thema)
        product_type1.save()

        product_type2 = ProductTypeFactory.create()
        product_type2.themas.add(self.thema)
        product_type2.save()

        response = self.client.get(self.path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        expected_data = [
            {
                "id": str(product_type1.id),
                "naam": product_type1.naam,
                "code": product_type1.code,
                "samenvatting": product_type1.samenvatting,
                "beschrijving": product_type1.beschrijving,
                "uniforme_product_naam": product_type1.uniforme_product_naam.naam,
                "toegestane_statussen": [],
                "vragen": [],
                "prijzen": [],
                "links": [],
                "bestanden": [],
                "locaties": [],
                "organisaties": [],
                "contacten": [],
                "eigenschappen": [],
                "externe_codes": [],
                "gepubliceerd": True,
                "aanmaak_datum": product_type1.aanmaak_datum.astimezone().isoformat(),
                "update_datum": product_type1.update_datum.astimezone().isoformat(),
                "keywords": [],
                "themas": [
                    {
                        "id": str(self.thema.id),
                        "naam": self.thema.naam,
                        "gepubliceerd": True,
                        "aanmaak_datum": self.thema.aanmaak_datum.astimezone().isoformat(),
                        "update_datum": self.thema.update_datum.astimezone().isoformat(),
                        "beschrijving": self.thema.beschrijving,
                        "hoofd_thema": self.thema.hoofd_thema,
                    }
                ],
            },
            {
                "id": str(product_type2.id),
                "naam": product_type2.naam,
                "code": product_type2.code,
                "samenvatting": product_type2.samenvatting,
                "beschrijving": product_type2.beschrijving,
                "uniforme_product_naam": product_type2.uniforme_product_naam.naam,
                "toegestane_statussen": [],
                "vragen": [],
                "prijzen": [],
                "links": [],
                "bestanden": [],
                "locaties": [],
                "organisaties": [],
                "contacten": [],
                "eigenschappen": [],
                "externe_codes": [],
                "gepubliceerd": True,
                "aanmaak_datum": product_type2.aanmaak_datum.astimezone().isoformat(),
                "update_datum": product_type2.update_datum.astimezone().isoformat(),
                "keywords": [],
                "themas": [
                    {
                        "id": str(self.thema.id),
                        "naam": self.thema.naam,
                        "gepubliceerd": True,
                        "aanmaak_datum": self.thema.aanmaak_datum.astimezone().isoformat(),
                        "update_datum": self.thema.update_datum.astimezone().isoformat(),
                        "beschrijving": self.thema.beschrijving,
                        "hoofd_thema": self.thema.hoofd_thema,
                    }
                ],
            },
        ]
        self.assertCountEqual(response.data["results"], expected_data)

    def test_read_product_type(self):
        product_type = ProductTypeFactory.create()
        product_type.themas.add(self.thema)
        product_type.save()

        response = self.client.get(self.detail_path(product_type))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {
            "id": str(product_type.id),
            "naam": product_type.naam,
            "code": product_type.code,
            "samenvatting": product_type.samenvatting,
            "beschrijving": product_type.beschrijving,
            "uniforme_product_naam": product_type.uniforme_product_naam.naam,
            "toegestane_statussen": [],
            "vragen": [],
            "prijzen": [],
            "links": [],
            "bestanden": [],
            "gepubliceerd": True,
            "aanmaak_datum": product_type.aanmaak_datum.astimezone().isoformat(),
            "update_datum": product_type.update_datum.astimezone().isoformat(),
            "keywords": [],
            "locaties": [],
            "organisaties": [],
            "contacten": [],
            "eigenschappen": [],
            "externe_codes": [],
            "themas": [
                {
                    "id": str(self.thema.id),
                    "naam": self.thema.naam,
                    "gepubliceerd": True,
                    "aanmaak_datum": self.thema.aanmaak_datum.astimezone().isoformat(),
                    "update_datum": self.thema.update_datum.astimezone().isoformat(),
                    "beschrijving": self.thema.beschrijving,
                    "hoofd_thema": self.thema.hoofd_thema,
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


class TestProductTypeFilterSet(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        self.path = reverse("producttype-list")

    def test_gepubliceerd_filter(self):
        ProductTypeFactory.create(gepubliceerd=True)
        ProductTypeFactory.create(gepubliceerd=False)

        response = self.client.get(self.path + "?gepubliceerd=true")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_uniforme_product_naam_filter(self):
        ProductTypeFactory.create(
            uniforme_product_naam=UniformeProductNaamFactory(naam="parkeervergunning")
        )
        ProductTypeFactory.create(
            uniforme_product_naam=UniformeProductNaamFactory(naam="aanleunwoning")
        )

        response = self.client.get(
            self.path + "?uniforme_product_naam=parkeervergunning"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_eigenschap_filter(self):
        product_type_1 = ProductTypeFactory.create()
        EigenschapFactory(
            naam="doelgroep", waarde="inwoner", product_type=product_type_1
        )

        product_type_2 = ProductTypeFactory.create()
        EigenschapFactory(
            naam="doelgroep", waarde="verenigingen", product_type=product_type_2
        )

        response = self.client.get(self.path + "?eigenschap=[doelgroep:inwoner]")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_eigenschap_filter_without_brackets(self):
        response = self.client.get(self.path + "?eigenschap=abc")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_eigenschap_filter_without_key_value(self):
        response = self.client.get(self.path + "?eigenschap=[:]")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_eigenschap_filter_with_invalid_charakters(self):
        response = self.client.get(self.path + "?eigenschap=[a[b:[b:a]]")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_externe_code_filter(self):
        product_type_1 = ProductTypeFactory.create()
        ExterneCodeFactory(naam="ISO", code="12345", product_type=product_type_1)

        product_type_2 = ProductTypeFactory.create()
        EigenschapFactory(naam="ISO", waarde="9837549857", product_type=product_type_2)

        response = self.client.get(self.path + "?externe_code=[ISO:12345]")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_externe_code_filter_without_brackets(self):
        response = self.client.get(self.path + "?externe_code=abc")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_externe_code_filter_without_key_value(self):
        response = self.client.get(self.path + "?externe_code=[:]")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_externe_code_filter_with_invalid_charakters(self):
        response = self.client.get(self.path + "?externe_code=[a[b:[b:a]]")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
