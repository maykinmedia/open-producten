from open_api_framework.conf.base import *
from open_api_framework.conf.utils import config

init_sentry()

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/
TIME_ZONE = "Europe/Amsterdam"  # note: this *may* affect the output of DRF datetimes

INSTALLED_APPS += [
    # 'django.contrib.admindocs',
    # 'django.contrib.humanize',
    # 'django.contrib.sitemaps',
    # External applications.
    # 'hijack',
    # 'hijack.contrib.admin',
    # Project applications.
    "treebeard",
    "open_producten.accounts",
    "open_producten.utils",
    "open_producten.producttypes",
]

MIDDLEWARE += [
    # 'django.middleware.locale.LocaleMiddleware',
    # 'hijack.middleware.HijackUserMiddleware',
]

#
# FIXTURES
#

FIXTURE_DIRS = (DJANGO_PROJECT_DIR / "fixtures",)

#
# Custom settings
#
PROJECT_NAME = "open_producten"
SHOW_ALERT = True
ENABLE_ADMIN_NAV_SIDEBAR = config("ENABLE_ADMIN_NAV_SIDEBAR", default=False)

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

#
# DJANGO-HIJACK
#
# HIJACK_PERMISSION_CHECK = 'maykin_2fa.hijack.superusers_only_and_is_verified'
# HIJACK_INSERT_BEFORE = (
#     '<div class='content'>'  # note that this only applies to the admin
# )
