from django.apps import apps
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.views.generic.base import RedirectView

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from maykin_2fa import monkeypatch_admin
from maykin_2fa.urls import urlpatterns, webauthn_urlpatterns
from mozilla_django_oidc_db.views import AdminLoginFailure

from open_producten.accounts.views.password_reset import PasswordResetView

# from open_producten.locations.router import location_urlpatterns
# from open_producten.products.router import product_urlpatterns
# from open_producten.producttypen.router import product_type_urlpatterns

# Configure admin

monkeypatch_admin()

handler500 = "open_producten.utils.views.server_error"

admin.site.enable_nav_sidebar = False
admin.site.site_header = "Open Producten admin"
admin.site.site_title = "Open Producten admin"
admin.site.index_title = "Open Producten dashboard"

# URL routing

urlpatterns = [
    path(
        "admin/password_reset/",
        PasswordResetView.as_view(),
        name="admin_password_reset",
    ),
    path(
        "admin/password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    # OIDC urls
    path("admin/login/failure/", AdminLoginFailure.as_view(), name="admin-oidc-error"),
    path("auth/oidc/", include("mozilla_django_oidc.urls")),
    # Use custom login views for the admin + support hardware tokens
    path("admin/", include((urlpatterns, "maykin_2fa"))),
    path("admin/", include((webauthn_urlpatterns, "two_factor"))),
    path("admin/", admin.site.urls),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    # redirect root to admin index.
    path("", RedirectView.as_view(pattern_name="admin:index")),
    path(
        "api/v1/",
        include(
            [
                path(
                    "schema/",
                    SpectacularAPIView.as_view(schema=None),
                    name="schema",
                ),
                path(
                    "schema/swagger-ui/",
                    SpectacularSwaggerView.as_view(url_name="schema"),
                    name="swagger-ui",
                ),
                path(
                    "schema/redoc/",
                    SpectacularRedocView.as_view(url_name="schema"),
                    name="redoc",
                ),
                # path("", include(product_type_urlpatterns)),
                # path("", include(product_urlpatterns)),
                # path("", include(location_urlpatterns)),
            ]
        ),
    ),
    path("tinymce/", include("tinymce.urls")),
]

# NOTE: The staticfiles_urlpatterns also discovers static files (ie. no need to run collectstatic). Both the static
# folder and the media folder are only served via Django if DEBUG = True.
urlpatterns += staticfiles_urlpatterns() + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)

if settings.DEBUG and apps.is_installed("debug_toolbar"):
    import debug_toolbar

    urlpatterns = [
                      path("__debug__/", include(debug_toolbar.urls)),
                  ] + urlpatterns
