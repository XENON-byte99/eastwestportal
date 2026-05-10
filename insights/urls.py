from django.urls import path
from . import views

app_name = 'insights'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_insight, name='create'),
    path('update/<int:pk>/', views.update_insight, name='update'),
    path('delete/<int:pk>/', views.delete_insight, name='delete'),
    
    # API
    path('api/insights/<int:insight_id>/comments/', views.api_add_comment, name='api_add_comment'),
    path('api/comments/<int:comment_id>/', views.api_comment_detail, name='api_comment_detail'),
]
