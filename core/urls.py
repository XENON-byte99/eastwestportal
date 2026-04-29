from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Dashboard moved to /dashboard/
    path('dashboard/', views.home, name='home'),
    path('pending/', views.pending_approval, name='pending_approval'),
    path('enrollment/', views.enrollment_view, name='enrollment'),
    path('my-uploads/', views.my_uploads, name='my_uploads'),
    path('logout/', views.logout_view, name='logout'),

    
    # Management - Users & Faculty
    path('manage/users/', views.manage_users, name='manage_users'),
    path('api/users/', views.api_user_manage, name='api_user_manage'),
    path('api/users/<int:user_id>/', views.api_user_manage, name='api_user_delete'),

    # Global Search API
    path('api/search/', views.global_search_api, name='global_search_api'),
    
    # Moderation Dashboard
    path('moderation/', views.moderation_dashboard, name='moderation_dashboard'),
    path('moderation/approve/<str:model_name>/<int:obj_id>/', views.approve_item, name='approve_item'),
    path('moderation/reject/<str:model_name>/<int:obj_id>/', views.reject_item, name='reject_item'),
    path('moderation/announcement/create/', views.api_create_announcement, name='create_announcement'),
    
    # Notifications

    path('api/notifications/', views.api_notifications, name='api_notifications'),
    path('api/notifications/read/', views.api_notifications_read, name='api_notifications_read'),
]

