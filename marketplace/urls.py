from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('', views.index, name='index'),
    # JSON API
    path('api/listings/', views.api_listings, name='api_listings'),
    path('api/listings/<int:listing_id>/', views.api_listing_detail, name='api_listing_detail'),
    path('api/listings/<int:listing_id>/chat/', views.api_chat, name='api_chat'),
]
