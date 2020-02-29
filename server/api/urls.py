from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include
from rest_framework import routers, permissions
from django.conf import settings
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

from api.views.user import UserViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"users", UserViewSet, basename="users")

schema_view = get_schema_view(
    openapi.Info(title="Arriva Service API", default_version="v1"),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    url(r"^", include(router.urls)),
    url(r"^authorize/", obtain_jwt_token),
    url(r"^refresh-token/", refresh_jwt_token),
    url(r"^documentation/$", schema_view.with_ui("redoc", cache_timeout=None), name="schema-redoc",),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [url(r"^__debug__/", include(debug_toolbar.urls))]

urlpatterns += staticfiles_urlpatterns()
