# """
# URL configuration for config project.

# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/5.2/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# """
# from django.contrib import admin
# from django.urls import path

# # urlpatterns = [
# # ]



# # config/urls.py
# # from django.conf import settings
# # from django.conf.urls.static import static
# # from django.contrib import admin
# # from django.urls import path, include
# # from django.conf.urls.static import static
# # urlpatterns = [
# #     path('admin/', admin.site.urls),
# #     path('api/accounts/', include('apps.accounts.urls')),
# #     path('api/profiles/', include('apps.profiles.urls')),
# #     path('api/stories/', include('apps.stories.urls')),      
# #     path('api/messages/', include('apps.messaging.urls')),  
# #     path('api/hashtags/', include('apps.hashtags.urls')),    
# #     path('api/blocks/', include('apps.blocks.urls')),
# #     path('api/ml/', include('apps.ml.urls')),
    
# #     path('admin/ml/analyze/<str:user_id>/', include('apps.ml.urls')),
   

#     #path('admin/ml/', include('apps.ml.urls')),
#     #path('admin/ml/', include('apps.ml.admin_urls')),

#     #     path('api/ml/', include('apps.ml.urls')),  # مسیر API برای ml
#     # # اضافه کردن مسیر مستقیم برای تحلیل کاربران در admin
#     # path('admin/ml/analyze/<str:user_id>/', 
#     #      include('apps.ml.urls')),  # یا مستقیماً ویو را import کنید



# # ]
# # if settings.DEBUG:
# #     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)





# # config/urls.py
# from django.conf import settings
# from django.conf.urls.static import static
# from django.contrib import admin
# from django.urls import path, include
# from apps.ml.views import AdminAnalyzeUserView

# urlpatterns = [
#     path('admin/ml/analyze/<str:user_id>/', AdminAnalyzeUserView.as_view(), name='admin_analyze'),
#     path('admin/', admin.site.urls),
#     path('admin/ml/analyze/<str:user_id>/', AdminAnalyzeUserView.as_view(), name='admin_analyze'),

    
#     path('api/accounts/', include('apps.accounts.urls')),
#     path('api/profiles/', include('apps.profiles.urls')),
#     path('api/stories/', include('apps.stories.urls')),      
#     path('api/messages/', include('apps.messaging.urls')),  
#     path('api/hashtags/', include('apps.hashtags.urls')),    
#     path('api/blocks/', include('apps.blocks.urls')),
#     path('api/ml/', include('apps.ml.urls')),
#     path('api/posts/', include('apps.posts.urls')),
#     path('api/ml/', include('apps.ml.urls')),  
 

# ]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)










# from django.conf import settings
# from django.conf.urls.static import static
# from django.contrib import admin
# from django.urls import path, include
# from apps.ml.views import AdminAnalyzeUserView

# urlpatterns = [
#     # Admin URLs
#     path('admin/', admin.site.urls),
#     path('admin/ml/analyze/<str:user_id>/', AdminAnalyzeUserView.as_view(), name='admin_analyze'),
    
#     # API URLs
#     path('api/accounts/', include('apps.accounts.urls')),
#     path('api/profiles/', include('apps.profiles.urls')),
#     path('api/stories/', include('apps.stories.urls')),      
#     path('api/messages/', include('apps.messaging.urls')),  
#     path('api/hashtags/', include('apps.hashtags.urls')),    
#     path('api/blocks/', include('apps.blocks.urls')),
#     path('api/ml/', include('apps.ml.urls')), 
#     path('api/posts/', include('apps.posts.urls')),
#     path('ml/', include('apps.ml.urls')), 
#     path('admin/ml/analyze/<str:user_id>/', AdminAnalyzeUserView.as_view(), name='admin_analyze'),
#     path('admin/', admin.site.urls),
#     path('admin/ml/analyze/<str:user_id>/', AdminAnalyzeUserView.as_view(), name='admin_analyze'),


# ]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from apps.ml.views import AdminAnalyzeUserView  # اضافه کن
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('admin/analyze-user/<str:user_id>/', AdminAnalyzeUserView.as_view(), name='admin-analyze-user'),

    path('admin/', admin.site.urls),
    
    
    # API URLs
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/profiles/', include('apps.profiles.urls')),
    path('api/stories/', include('apps.stories.urls')),      
    path('api/messages/', include('apps.messaging.urls')),  
    path('api/hashtags/', include('apps.hashtags.urls')),    
    path('api/blocks/', include('apps.blocks.urls')),
    path('api/ml/', include('apps.ml.urls')), 
    path('api/posts/', include('apps.posts.urls')),
    path('ml/', include('apps.ml.urls')), 
    path('admin/ml/analyze/<str:user_id>/', AdminAnalyzeUserView.as_view(), name='admin_analyze_old'),
    path('api/search/', include('apps.search.urls')),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),


]







if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)