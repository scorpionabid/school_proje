from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Test URLs for different permission levels
    path('admin-only/', views.admin_only_view, name='admin_only'),
    path('region-admin/', views.region_admin_view, name='region_admin'),
    path('sector-admin/', views.sector_admin_view, name='sector_admin'),
    path('school-admin/', views.school_admin_view, name='school_admin'),
]
