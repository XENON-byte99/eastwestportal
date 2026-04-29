from django.urls import path
from . import views

app_name = 'feed'

urlpatterns = [
    path('', views.index, name='index'),
    # JSON API
    path('api/posts/', views.api_posts, name='api_posts'),
    path('api/posts/<int:post_id>/', views.api_post_detail, name='api_post_detail'),
    path('api/posts/<int:post_id>/like/', views.api_like_post, name='api_like_post'),
    path('api/posts/<int:post_id>/comments/', views.api_comments, name='api_comments'),
    path('api/comments/<int:comment_id>/', views.api_comment_detail, name='api_comment_detail'),
]
