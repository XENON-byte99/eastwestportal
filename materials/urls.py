from django.urls import path
from . import views

app_name = 'materials'

urlpatterns = [
    path('', views.index, name='index'),
    path('manage/', views.manage_courses, name='manage_courses'),
    path('manage/types/', views.manage_material_types, name='manage_types'),
    
    # JSON API
    path('api/materials/', views.api_materials, name='api_materials'),
    path('api/materials/<int:material_id>/', views.api_material_detail, name='api_material_detail'),
    path('api/materials/<int:material_id>/rate/', views.api_rate_material, name='api_rate_material'),
    path('api/attachments/<int:attachment_id>/', views.api_attachment_delete, name='api_attachment_delete'),
    path('api/courses/', views.api_courses, name='api_courses'),

    path('api/courses/manage/', views.api_course_manage, name='api_course_manage'),
    path('api/courses/manage/<int:course_id>/', views.api_course_manage, name='api_course_delete'),
    
    path('api/types/manage/', views.api_material_type_manage, name='api_type_manage'),
    path('api/types/manage/<int:type_id>/', views.api_material_type_manage, name='api_type_delete'),
]
