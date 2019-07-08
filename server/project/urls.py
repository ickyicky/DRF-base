from django.conf import settings
from django.urls import include
from rest_framework import routers, permissions
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from project.views.user import UserViewSet
from project.views.token import TokenViewSet, TokenRefreshViewSet
from project.views.cookie import CookieViewSet
from project.views.password import (
    ResetPasswordViewSet,
    ChangePasswordViewSet,
    RestorePasswordViewSet,
    RestoreDefaultPasswordViewSet,
)

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"users", UserViewSet, base_name="users")


schema_view = get_schema_view(
    openapi.Info(title="project Service API", default_version="v1"),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    url(r"^", include(router.urls)),
    url(regex=r"^token$", view=TokenViewSet.as_view({"post": "create"}), name="token"),
    url(
        regex=r"^cookie$",
        view=CookieViewSet.as_view({"post": "sign_in", "delete": "sign_out"}),
        name="cookie",
    ),
    url(
        regex=r"^token/refresh$",
        view=TokenRefreshViewSet.as_view({"post": "refresh"}),
        name="token-refresh",
    ),
    url(
        regex=r"^users/me/restore_password$",
        view=RestorePasswordViewSet.as_view({"post": "restore_password"}),
        name="user-restore_password",
    ),
    url(
        regex=r"^users/default/(?P<user_id>[^/.]+)/restore_password$",
        view=RestoreDefaultPasswordViewSet.as_view({"post": "restore_password"}),
        name="user-restore_default_password",
    ),
    url(
        regex=r"^users/me/change_password$",
        view=ChangePasswordViewSet.as_view({"post": "change_password"}),
        name="user-change_password",
    ),
    url(
        r"^documentation/$",
        schema_view.with_ui("redoc", cache_timeout=None),
        name="schema-redoc",
    ),
    url(
        regex=r"^reset_password/(?P<token>.+)/$",
        view=ResetPasswordViewSet.as_view(),
        name="reset_password",
    ),
]
urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [url(r"^__debug__/", include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
