from django.contrib.auth.models import AnonymousUser
from django.template import Context, Template
from django.test import SimpleTestCase, override_settings

from open_producten.accounts.tests.factories import UserFactory


@override_settings(SHOW_ENVIRONMENT=True)
class EnvironmentInfoTests(SimpleTestCase):

    def _render(self, context=None):
        tpl = Template(
            """
            {%load utils%}
            {% show_environment_info %}
        """
        )
        return tpl.render(Context(context or {})).strip()

    @override_settings(SHOW_ENVIRONMENT=False)
    def test_disabled_via_settings(self):
        with self.subTest("without user"):
            result = self._render()

            self.assertEqual(result, "")

        with self.subTest("with user"):
            result = self._render({"user": UserFactory.build()})

            self.assertEqual(result, "")

    def test_anonymous_user(self):
        result = self._render({"user": AnonymousUser()})

        self.assertEqual(result, "")

    @override_settings(ENVIRONMENT_LABEL="my super duper env")
    def test_authenticated_user(self):
        result = self._render({"user": UserFactory.build()})

        self.assertNotEqual(result, "")
        self.assertInHTML("my super duper env", result)
