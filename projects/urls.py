from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.index, name='index'),
    # JSON API
    path('api/areas/', views.api_research_areas, name='api_research_areas'),
    path('api/papers/', views.api_papers, name='api_papers'),
    path('api/capstones/', views.api_capstones, name='api_capstones'),
    path('api/papers/<int:paper_id>/', views.api_paper_detail, name='api_paper_detail'),
    path('api/capstones/<int:capstone_id>/', views.api_capstone_detail, name='api_capstone_detail'),
]
