from rest_framework.routers import DefaultRouter, SimpleRouter
from django.conf import settings
from sme_atualizacao_cadastral_apps.users.api.viewsets import UserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)


app_name = "api"
urlpatterns = router.urls
