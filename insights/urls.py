from django.urls import path
from . import views

app_name = 'insights'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_insight, name='create'),
    path('delete/<int:pk>/', views.delete_insight, name='delete'),
]
