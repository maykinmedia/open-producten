from django.utils.translation import gettext_lazy as _

from celery.schedules import crontab
from open_api_framework.conf.base import *
from open_api_framework.conf.utils import config

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = "nl-nl"

TIME_ZONE = "Europe/Amsterdam"  # note: this *may* affect the output of DRF datetimes

INSTALLED_APPS += [
    # 'django.contrib.admindocs',
    # 'django.contrib.humanize',
    # 'django.contrib.sitemaps',
    # External applications.
    # Project applications.
    "rest_framework.authtoken",
    "timeline_logger",
    "localflavor",
    "parler",
    "markdownx",
    "django_celery_beat",
    "open_producten.accounts",
    "open_producten.logging",
    "open_producten.utils",
    "open_producten.producttypen",
    "open_producten.producten",
    "open_producten.locaties",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", PROJECT_DIRNAME),
        "USER": config("DB_USER", PROJECT_DIRNAME),
        "PASSWORD": config("DB_PASSWORD", PROJECT_DIRNAME),
        "HOST": config("DB_HOST", "localhost"),
        "PORT": config("DB_PORT", 5432),
    }
}

MIDDLEWARE.insert(
    MIDDLEWARE.index("django.middleware.common.CommonMiddleware"),
    "django.middleware.locale.LocaleMiddleware",
)

#
# CELERY
#

# amount of days to keep when the 'Prune timeline logs' task is called.
PRUNE_LOGS_TASK_KEEP_DAYS = 30

CELERY_BROKER_URL = "redis://localhost:6379"  # Redis broker
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_BEAT_SCHEDULE = {
    "Update product statussen": {
        "task": "open_producten.producten.tasks.set_product_states",
        "schedule": crontab(minute="0", hour="0"),
    },
    "Prune timeline logs": {
        "task": "open_producten.logging.tasks.prune_logs",
        "schedule": crontab(minute="0", hour="0", day_of_month="1"),
        "args": (PRUNE_LOGS_TASK_KEEP_DAYS,),
    },
}


#
# Custom settings
#
SITE_TITLE = "API dashboard"
PROJECT_NAME = "Open Producten"
SHOW_ALERT = True

# This setting is used by the csrf_failure view (accounts app).
# You can specify any path that should match the request.path
# Note: the LOGIN_URL Django setting is not used because you could have
# multiple login urls defined.
LOGIN_URLS = [reverse_lazy("admin:login")]

# Default (connection timeout, read timeout) for the requests library (in seconds)
REQUESTS_DEFAULT_TIMEOUT = (10, 30)

##############################
#                            #
# 3RD PARTY LIBRARY SETTINGS #
#                            #
##############################

#
# Django-Admin-Index
#
ADMIN_INDEX_DISPLAY_DROP_DOWN_MENU_CONDITION_FUNCTION = (
    "open_producten.utils.django_two_factor_auth.should_display_dropdown_menu"
)

ADMIN_INDEX_SHOW_REMAINING_APPS = False

#
# markdownx
#
MARKDOWNX_EDITOR_RESIZABLE = False

#
# Django rest framework
#
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_SCHEMA_CLASS": "open_producten.utils.schema.AutoSchema",
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_PAGINATION_CLASS": "open_producten.utils.pagination.Pagination",
    "PAGE_SIZE": 100,
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "NON_FIELD_ERRORS_KEY": "model_errors",
    "DEFAULT_FILTER_BACKENDS": ["open_producten.utils.filters.FilterBackend"],
}

PRODUCTEN_API_VERSION = "0.0.1"
PRODUCTTYPEN_API_VERSION = "0.0.1"

PRODUCTEN_API_MAJOR_VERSION = PRODUCTEN_API_VERSION.split(".")[0]
PRODUCTTYPEN_API_MAJOR_VERSION = PRODUCTTYPEN_API_VERSION.split(".")[0]

#
# SPECTACULAR - OpenAPI schema generation
#

OPEN_PRODUCTEN_API_CONTACT_EMAIL = "support@maykinmedia.nl"
OPEN_PRODUCTEN_API_CONTACT_URL = "https://www.maykinmedia.nl"

SPECTACULAR_SETTINGS = {  # TODO: may need to be expanded.
    "SCHEMA_PATH_PREFIX": "/api/v1",
    "TITLE": "Open Producten API",
    "LICENSE": {"name": "EUPL 1.2", "url": "https://opensource.org/licenses/EUPL-1.2"},
    "CONTACT": {
        "email": OPEN_PRODUCTEN_API_CONTACT_EMAIL,
        "url": OPEN_PRODUCTEN_API_CONTACT_URL,
    },
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
    "SERVE_INCLUDE_SCHEMA": False,
    "POSTPROCESSING_HOOKS": (
        "drf_spectacular.hooks.postprocess_schema_enums",
        "open_producten.utils.spectacular_hooks.custom_postprocessing_hook",
    ),
    "COMPONENT_SPLIT_REQUEST": True,
}

# Subpath (optional)
# This environment variable can be configured during deployment.
SUBPATH = config("SUBPATH", None)
if SUBPATH:
    SUBPATH = f"/{SUBPATH.strip('/')}"


LANGUAGES = [
    ("nl", _("Dutch")),
    ("en", _("English")),
]

PARLER_LANGUAGES = {
    1: (
        {
            "code": "nl",
        },
        {
            "code": "en",
        },
    ),
    "default": {
        "fallbacks": ["nl"],
        "hide_untranslated": False,
    },
}

FORCE_TRANSLATION_STRINGS = [
    _("A page number within the paginated result set."),
    _("Number of results to return per page."),
]
