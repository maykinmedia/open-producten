from django.urls import reverse

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient

from open_producten.producttypen.models import Onderwerp, Vraag
from open_producten.producttypen.tests.factories import (
    OnderwerpFactory,
    ProductTypeFactory,
    VraagFactory,
)
from open_producten.utils.tests.cases import BaseApiTestCase


class TestOnderwerpViewSet(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        self.data = {
            "naam": "test-onderwerp",
            "hoofd_onderwerp": None,
            "product_type_ids": [],
        }
        self.path = reverse("onderwerp-list")

    def detail_path(self, onderwerp):
        return reverse("onderwerp-detail", args=[onderwerp.id])

    def test_read_onderwerp_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_required_fields(self):
        response = self.client.post(self.path, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "naam": [ErrorDetail(string="Dit veld is vereist.", code="required")],
                "product_type_ids": [
                    ErrorDetail(string="Dit veld is vereist.", code="required")
                ],
                "hoofd_onderwerp": [
                    ErrorDetail(string="Dit veld is vereist.", code="required")
                ],
            },
        )

    def test_create_minimal_onderwerp(self):
        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Onderwerp.objects.count(), 1)
        onderwerp = Onderwerp.objects.first()
        expected_data = {
            "id": str(onderwerp.id),
            "naam": onderwerp.naam,
            "beschrijving": onderwerp.beschrijving,
            "vragen": [],
            "gepubliceerd": False,
            "hoofd_onderwerp": None,
            "product_typen": [],
            "aanmaak_datum": onderwerp.aanmaak_datum.astimezone().isoformat(),
            "update_datum": onderwerp.update_datum.astimezone().isoformat(),
        }
        self.assertEqual(response.data, expected_data)

    def test_create_onderwerp_with_hoofd_onderwerp(self):
        self.maxDiff = None
        hoofd_onderwerp = OnderwerpFactory.create()
        data = self.data | {"hoofd_onderwerp": hoofd_onderwerp.id}

        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Onderwerp.objects.count(), 2)

        onderwerp = Onderwerp.objects.get(id=response.data["id"])
        self.assertEqual(onderwerp.hoofd_onderwerp, hoofd_onderwerp)
        expected_data = {
            "id": str(onderwerp.id),
            "naam": onderwerp.naam,
            "beschrijving": onderwerp.beschrijving,
            "vragen": [],
            "gepubliceerd": False,
            "hoofd_onderwerp": onderwerp.hoofd_onderwerp.id,
            "product_typen": [],
            "aanmaak_datum": onderwerp.aanmaak_datum.astimezone().isoformat(),
            "update_datum": onderwerp.update_datum.astimezone().isoformat(),
        }
        self.assertEqual(response.data, expected_data)

    def test_create_onderwerp_with_product_type(self):
        product_type = ProductTypeFactory.create()
        data = self.data | {"product_type_ids": [product_type.id]}

        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Onderwerp.objects.count(), 1)
        self.assertEqual(
            list(Onderwerp.objects.values_list("product_typen", flat=True)),
            [product_type.id],
        )

    def test_create_hoofd_onderwerp_with_duplicate_product_typen_returns_error(self):
        product_type = ProductTypeFactory.create()
        data = self.data | {"product_type_ids": [product_type.id, product_type.id]}

        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "product_type_ids": [
                    ErrorDetail(
                        string=f"Dubbel id: {product_type.id} op index 1.",
                        code="invalid",
                    )
                ]
            },
        )

    def test_create_published_sub_onderwerp_with_unpublished_hoofd_onderwerp_returns_error(
        self,
    ):
        hoofd_onderwerp = OnderwerpFactory.create(gepubliceerd=False)

        data = self.data | {"hoofd_onderwerp": hoofd_onderwerp.id, "gepubliceerd": True}

        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "hoofd_onderwerp": [
                    ErrorDetail(
                        string="Onderwerpen moeten gepubliceerd zijn voordat sub-onderwerpen kunnen worden gepubliceerd.",
                        code="invalid",
                    )
                ]
            },
        )

    def test_update_change_from_root_to_hoofd_onderwerp(self):
        new_hoofd_onderwerp = OnderwerpFactory.create()
        onderwerp = OnderwerpFactory.create()

        data = self.data | {"hoofd_onderwerp": new_hoofd_onderwerp.id}
        response = self.client.put(self.detail_path(onderwerp), data)

        onderwerp.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(onderwerp.hoofd_onderwerp, new_hoofd_onderwerp)

    def test_update_change_from_hoofd_onderwerp_to_root(self):
        hoofd_onderwerp = OnderwerpFactory.create()
        onderwerp = OnderwerpFactory.create(
            naam="test-onderwerp", hoofd_onderwerp=hoofd_onderwerp
        )

        data = self.data | {"hoofd_onderwerp": None}
        response = self.client.put(self.detail_path(onderwerp), data)

        onderwerp.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(onderwerp.hoofd_onderwerp, None)

    def test_update_change_from_hoofd_onderwerp_to_hoofd_onderwerp(self):
        hoofd_onderwerp = OnderwerpFactory.create()
        onderwerp = OnderwerpFactory.create(
            naam="test-onderwerp", hoofd_onderwerp=hoofd_onderwerp
        )

        new_hoofd_onderwerp = OnderwerpFactory.create()

        data = self.data | {"hoofd_onderwerp": new_hoofd_onderwerp.id}
        response = self.client.put(self.detail_path(onderwerp), data)

        onderwerp.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(onderwerp.hoofd_onderwerp, new_hoofd_onderwerp)

    def test_update_hoofd_onderwerp_with_duplicate_product_typen_returns_error(self):
        onderwerp = OnderwerpFactory.create()
        product_type = ProductTypeFactory.create()
        data = self.data | {"product_type_ids": [product_type.id, product_type.id]}

        response = self.client.put(self.detail_path(onderwerp), data)

        onderwerp.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "product_type_ids": [
                    ErrorDetail(
                        string=f"Dubbel id: {product_type.id} op index 1.",
                        code="invalid",
                    )
                ]
            },
        )

    def test_update_unpublished_sub_onderwerp_to_published_with_unpublished_hoofd_onderwerp_returns_error(
        self,
    ):
        hoofd_onderwerp = OnderwerpFactory.create(gepubliceerd=False)
        sub_onderwerp = OnderwerpFactory.create(
            naam="sub onderwerp", hoofd_onderwerp=hoofd_onderwerp
        )

        data = self.data | {"hoofd_onderwerp": hoofd_onderwerp.id, "gepubliceerd": True}

        response = self.client.put(self.detail_path(sub_onderwerp), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "hoofd_onderwerp": [
                    ErrorDetail(
                        string="Onderwerpen moeten gepubliceerd zijn voordat sub-onderwerpen kunnen worden gepubliceerd.",
                        code="invalid",
                    )
                ]
            },
        )

    def test_update_published_hoofd_onderwerp_to_unpublished_with_published_sub_onderwerp_returns_error(
        self,
    ):
        hoofd_onderwerp = OnderwerpFactory.create(gepubliceerd=True)
        OnderwerpFactory.create(
            naam="sub onderwerp", hoofd_onderwerp=hoofd_onderwerp, gepubliceerd=True
        )

        data = self.data | {"hoofd_onderwerp": None, "gepubliceerd": False}

        response = self.client.put(self.detail_path(hoofd_onderwerp), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "hoofd_onderwerp": [
                    ErrorDetail(
                        string="Onderwerpen kunnen niet ongepubliceerd worden als ze gepubliceerde sub-onderwerpen hebben.",
                        code="invalid",
                    )
                ]
            },
        )

    def test_partial_update(self):
        hoofd_onderwerp = OnderwerpFactory.create()
        onderwerp = OnderwerpFactory.create(
            naam="test-onderwerp", hoofd_onderwerp=hoofd_onderwerp
        )

        data = {"naam": "update"}
        response = self.client.patch(self.detail_path(onderwerp), data)

        onderwerp.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(onderwerp.naam, "update")
        self.assertEqual(onderwerp.hoofd_onderwerp, hoofd_onderwerp)

    def test_partial_update_change_hoofd_onderwerp(self):
        hoofd_onderwerp = OnderwerpFactory.create()
        onderwerp = OnderwerpFactory.create(
            naam="test-onderwerp", hoofd_onderwerp=hoofd_onderwerp
        )

        new_hoofd_onderwerp = OnderwerpFactory.create()

        data = {"hoofd_onderwerp": new_hoofd_onderwerp.id}
        response = self.client.patch(self.detail_path(onderwerp), data)

        onderwerp.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(onderwerp.hoofd_onderwerp, new_hoofd_onderwerp)

    def test_partial_update_change_hoofd_onderwerp_to_root(self):
        hoofd_onderwerp = OnderwerpFactory.create()
        onderwerp = OnderwerpFactory.create(
            naam="test-onderwerp", hoofd_onderwerp=hoofd_onderwerp
        )

        data = {"hoofd_onderwerp": None}
        response = self.client.patch(self.detail_path(onderwerp), data)

        onderwerp.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(onderwerp.hoofd_onderwerp, None)

    def test_partial_update_hoofd_onderwerp_with_duplicate_product_typen_returns_error(
        self,
    ):
        onderwerp = OnderwerpFactory.create()
        product_type = ProductTypeFactory.create()
        data = {"product_type_ids": [product_type.id, product_type.id]}

        response = self.client.patch(self.detail_path(onderwerp), data)

        onderwerp.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "product_type_ids": [
                    ErrorDetail(
                        string=f"Dubbel id: {product_type.id} op index 1.",
                        code="invalid",
                    )
                ]
            },
        )

    def test_partial_update_unpublished_sub_onderwerp_to_published_with_unpublished_hoofd_onderwerp_returns_error(
        self,
    ):
        hoofd_onderwerp = OnderwerpFactory.create(gepubliceerd=False)
        sub_onderwerp = OnderwerpFactory.create(
            naam="sub onderwerp", hoofd_onderwerp=hoofd_onderwerp
        )

        data = {"gepubliceerd": True}

        response = self.client.patch(self.detail_path(sub_onderwerp), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "hoofd_onderwerp": [
                    ErrorDetail(
                        string="Onderwerpen moeten gepubliceerd zijn voordat sub-onderwerpen kunnen worden gepubliceerd.",
                        code="invalid",
                    )
                ]
            },
        )

    def test_partial_update_published_hoofd_onderwerp_to_unpublished_with_published_sub_onderwerp_returns_error(
        self,
    ):
        hoofd_onderwerp = OnderwerpFactory.create(gepubliceerd=True)
        OnderwerpFactory.create(
            naam="sub onderwerp", hoofd_onderwerp=hoofd_onderwerp, gepubliceerd=True
        )

        data = {"gepubliceerd": False}

        response = self.client.patch(self.detail_path(hoofd_onderwerp), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "hoofd_onderwerp": [
                    ErrorDetail(
                        string="Onderwerpen kunnen niet ongepubliceerd worden als ze gepubliceerde sub-onderwerpen hebben.",
                        code="invalid",
                    )
                ]
            },
        )

    def test_read_vraag(self):
        onderwerp = OnderwerpFactory.create()
        vraag = VraagFactory.create(onderwerp=onderwerp)

        response = self.client.get(self.detail_path(onderwerp))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = [
            {
                "id": str(vraag.id),
                "vraag": vraag.vraag,
                "antwoord": vraag.antwoord,
            }
        ]

        self.assertEqual(response.data["vragen"], expected_data)

    def test_read_product_type(self):
        onderwerp = OnderwerpFactory.create()
        product_type = ProductTypeFactory.create()
        onderwerp.product_typen.add(product_type)
        onderwerp.save()

        response = self.client.get(self.detail_path(onderwerp))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = [
            {
                "id": str(product_type.id),
                "naam": product_type.naam,
                "samenvatting": product_type.samenvatting,
                "beschrijving": product_type.beschrijving,
                "uniforme_product_naam": product_type.uniforme_product_naam.uri,
                "gepubliceerd": True,
                "aanmaak_datum": product_type.aanmaak_datum.astimezone().isoformat(),
                "update_datum": product_type.update_datum.astimezone().isoformat(),
                "keywords": [],
            }
        ]

        self.assertEqual(response.data["product_typen"], expected_data)

    def test_read_onderwerpen(self):
        onderwerp1 = OnderwerpFactory.create()
        onderwerp2 = OnderwerpFactory.create()

        response = self.client.get(self.path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        expected_data = [
            {
                "id": str(onderwerp1.id),
                "naam": onderwerp1.naam,
                "beschrijving": onderwerp1.beschrijving,
                "vragen": [],
                "gepubliceerd": True,
                "hoofd_onderwerp": None,
                "product_typen": [],
                "aanmaak_datum": onderwerp1.aanmaak_datum.astimezone().isoformat(),
                "update_datum": onderwerp1.update_datum.astimezone().isoformat(),
            },
            {
                "id": str(onderwerp2.id),
                "naam": onderwerp2.naam,
                "beschrijving": onderwerp2.beschrijving,
                "vragen": [],
                "gepubliceerd": True,
                "hoofd_onderwerp": None,
                "product_typen": [],
                "aanmaak_datum": onderwerp2.aanmaak_datum.astimezone().isoformat(),
                "update_datum": onderwerp2.update_datum.astimezone().isoformat(),
            },
        ]
        self.assertCountEqual(response.data["results"], expected_data)

    def test_read_onderwerp(self):
        onderwerp = OnderwerpFactory.create()

        response = self.client.get(self.detail_path(onderwerp))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {
            "id": str(onderwerp.id),
            "naam": onderwerp.naam,
            "beschrijving": onderwerp.beschrijving,
            "vragen": [],
            "gepubliceerd": True,
            "hoofd_onderwerp": None,
            "product_typen": [],
            "aanmaak_datum": onderwerp.aanmaak_datum.astimezone().isoformat(),
            "update_datum": onderwerp.update_datum.astimezone().isoformat(),
        }
        self.assertEqual(response.data, expected_data)

    def test_delete_onderwerp(self):
        onderwerp = OnderwerpFactory.create()
        VraagFactory.create(onderwerp=onderwerp)

        response = self.client.delete(self.detail_path(onderwerp))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Onderwerp.objects.count(), 0)
        self.assertEqual(Vraag.objects.count(), 0)

    def test_delete_onderwerp_when_linked_product_type_has_one_onderwerp(self):
        onderwerp = OnderwerpFactory.create()
        product_type = ProductTypeFactory.create(naam="test")
        product_type.onderwerpen.add(onderwerp)
        product_type.save()

        response = self.client.delete(self.detail_path(onderwerp))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "product_typen": [
                    "Product Type test moet aan een minimaal één onderwerp zijn gelinkt."
                ]
            },
        )

    def test_delete_onderwerp_when_linked_product_type_has_other_onderwerpen(self):
        onderwerp = OnderwerpFactory.create()
        product_type = ProductTypeFactory.create(naam="test")
        product_type.onderwerpen.add(onderwerp)
        product_type.onderwerpen.add(OnderwerpFactory())
        product_type.save()

        response = self.client.delete(self.detail_path(onderwerp))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Onderwerp.objects.count(), 1)
