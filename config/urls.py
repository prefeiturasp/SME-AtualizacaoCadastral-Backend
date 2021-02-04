import environ

from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib import admin
from django.views import defaults as default_views
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_swagger.views import get_swagger_view
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

from sme_atualizacao_cadastral_apps.core.api.urls import urlpatterns as url_core, router
from sme_atualizacao_cadastral_apps.alunos.urls import urlpatterns as url_alunos
from sme_atualizacao_cadastral_apps.users.urls import urlpatterns as url_users
from des import urls as des_url

env = environ.Env()

schema_view = get_swagger_view(title='API de Portal Uniformes', url=env.str('DJANGO_API_URL', default=''))

path_name = "api"

urlpatterns = [
    path(f"{path_name}/docs/", schema_view, name='docs'),
    # Django Admin, use {% url 'admin:index' %}
    path(f"{path_name}/{settings.ADMIN_URL}", admin.site.urls),
    # User management
    path(f"{path_name}/accounts/", include("allauth.urls")),
    path(f"{path_name}/django-des/", include(des_url)),
    # Your stuff: custom urls includes go here
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# API URLS
urlpatterns += [
    # API base url
    path("api/", include("config.api_router")),
    # DRF auth token
    path(f"{path_name}/auth-token/", obtain_auth_token),
    path(f"{path_name}/api-token-auth/", obtain_jwt_token),
    path(f"{path_name}/api-token-refresh/", refresh_jwt_token),
    path(f"{path_name}/", include(router.urls))
]

# urlpatterns += url_core
# urlpatterns += url_alunos
# urlpatterns += url_users

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
