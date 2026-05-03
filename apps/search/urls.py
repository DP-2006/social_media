# apps/search/urls.py

from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    path('', views.GlobalSearchView.as_view(), name='global-search'),
    path('config/', views.SearchConfigView.as_view(), name='search-config'),
]