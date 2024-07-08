from django.test import TestCase
from django.urls import NoReverseMatch, reverse

from .factories import UserFactory


class HijackSecurityTests(TestCase):

    def test_cannot_hijack_without_second_factor(self):
        staff_user = UserFactory.create(is_staff=True)
        superuser = UserFactory.create(superuser=True)
        superuser.totpdevice_set.create()
        self.client.force_login(superuser)

        # sanity check - MFA is being enforced
        admin_index_response = self.client.get(reverse("admin:index"))
        assert (
            admin_index_response.status_code == 302
        ), "Non-verified user unexpected has access to the admin"

        # try the hijack
        acquire = self.client.post(
            reverse("hijack:acquire"),
            data={"user_pk": staff_user.pk},
        )

        with self.subTest("hijack blocked"):
            # bad request due to SuspiciousOperation or 403 from PermissionDenied
            self.assertIn(acquire.status_code, [400, 403])

        with self.subTest("release does not allow gaining verified state"):
            # release the user
            release = self.client.post(reverse("hijack:release"))

            with self.subTest("release blocked due to hijack not being acquired"):
                self.assertEqual(release.status_code, 403)

            with self.subTest("no access to admin gained"):
                # due to bypass via release action which sets up a device
                admin_response = self.client.get(reverse("admin:index"))

                self.assertNotEqual(admin_response.status_code, 200)

    def test_drf_login_url_not_enabled(self):
        """
        The DRF login view may not be enabled, as this bypasses MFA.
        """
        try:
            reverse("rest_framework:login")
        except NoReverseMatch:
            pass
        else:
            self.fail("The DRF login view is exposed, which bypasses MFA!")
