# apps/search/urls.py

from django.urls import path
from . import views

app_name = 'search'
# apps/search/urls.py

from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    # جستجوی عمومی
    path('', views.GlobalSearchView.as_view(), name='global-search'),
    
    # جستجوی کاربران
    path('users/', views.SearchUsersView.as_view(), name='search-users'),
    path('user/<str:username>/', views.SearchByUsernameView.as_view(), name='search-by-username'),
    path('user/', views.SearchByUsernameView.as_view(), name='search-by-username-query'),
    
    # جستجوی پست‌ها و هشتگ‌ها
    path('posts/', views.SearchPostsView.as_view(), name='search-posts'),
    path('hashtags/', views.SearchHashtagsView.as_view(), name='search-hashtags'),
    
    # پیشنهادات و تنظیمات
    path('suggestions/', views.SearchSuggestionsView.as_view(), name='search-suggestions'),
    path('config/', views.SearchConfigView.as_view(), name='search-config'),
]


