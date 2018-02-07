from django.conf.urls import url
from . import views

app_name = 'core'

urlpatterns = [
    url(r'^$', views.QueryFormView.as_view(), name="index"),
]
