"""authors URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import include, path
from django.contrib import admin

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.documentation import include_docs_urls

schema_view = get_schema_view(
   openapi.Info(
      title="Author\'s Haven API",
      default_version='v1',
      description="This Documentation contains clear descriptions of all the API endpoints of the Author's Haven app.\
           It clearly gives all the neccessary payloads and possible responses for each endpoint.",
      contact=openapi.Contact(email="thy.realers@gmail.com"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

# To counter the error namespace error
app_name = 'authentication'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(('authors.apps.authentication.urls',
                          'authentication'), namespace='authentication')),
    path('api/', include(('authors.apps.articles.urls',
                            'articles'), namespace='articles')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('docs/', include_docs_urls(title='Author\'s Haven API')),
    path('api/profiles/', include('authors.apps.profiles.urls', namespace='profiles')),

]