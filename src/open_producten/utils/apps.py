from django.apps import AppConfig


class UtilsConfig(AppConfig):
    name = "open_producten.utils"

    def ready(self):
        from . import checks  # noqa
