"""FishTrackerDjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
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
import rest_framework
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.authtoken import views
from fishtracker import views as ft_views
from graphene_django.views import GraphQLView
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (api_view, authentication_classes,
                                       permission_classes)
from rest_framework.permissions import IsAuthenticated
from fishtracker.schema import schema



class RTGraphQLView(GraphQLView):

    def parse_body(self, request):
        if type(request) is rest_framework.request.Request:
            return request.data
        return super().parse_body(request)


def graphql_token_view():
    view = RTGraphQLView.as_view(schema=schema)
    view = permission_classes((IsAuthenticated,))(view)
    view = authentication_classes((TokenAuthentication,))(view)
    view = api_view(['POST'])(view)
    return view


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^graphql$', graphql_token_view()),
    url(r'^token$', views.obtain_auth_token),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # needs to be protected in production
    url(r'^graphiql$', GraphQLView.as_view(graphiql=True)),
]
