from django.urls import path
from . import views

app_name = 'region'

urlpatterns = [
    path('', views.region_list, name='region_list'),
    path('<int:pk>/', views.region_detail, name='region_detail'),
    path('<int:pk>/documents/', views.region_documents, name='region_documents'),
    path('<int:pk>/news/', views.region_news, name='region_news'),
    path('<int:pk>/statistics/', views.region_statistics, name='region_statistics'),
]
