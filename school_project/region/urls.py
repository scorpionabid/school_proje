from django.urls import path
from . import views

app_name = 'region'

urlpatterns = [
    path('dashboard/', views.region_dashboard, name='dashboard'),
]
