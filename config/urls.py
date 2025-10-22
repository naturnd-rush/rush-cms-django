"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView

from rush import views
from rush.graphql import get_schema

urlpatterns = [
    path("login/", views.rush_login_view),
    path("summernote/", include("django_summernote.urls")),
    path("_nested_admin/", include("nested_admin.urls")),
    path(
        # TODO: Remove csrf exempt here and add the token to internal graphQL requests!
        "graphql/",
        csrf_exempt(GraphQLView.as_view(graphiql=True, schema=get_schema())),
    ),
    path("", admin.site.urls),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
