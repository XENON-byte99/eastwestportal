from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    
    # Root redirects to feed
    path('', lambda request: redirect('feed:index')),
    
    path('core/', include('core.urls', namespace='core')),
    path('feed/', include('feed.urls', namespace='feed')),
    path('materials/', include('materials.urls', namespace='materials')),
    path('marketplace/', include('marketplace.urls', namespace='marketplace')),
    path('projects/', include('projects.urls', namespace='projects')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
