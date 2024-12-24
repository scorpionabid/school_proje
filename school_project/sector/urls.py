from django.urls import path
from . import views

app_name = 'sector'

urlpatterns = [
    # Sektor əməliyyatları
    path('dashboard/', views.sector_dashboard, name='dashboard'),
    path('', views.sector_list, name='list'),
    path('<int:sector_id>/', views.sector_detail, name='detail'),
    path('<int:sector_id>/statistics/', views.sector_statistics, name='statistics'),
    path('<int:sector_id>/reports/', views.sector_reports, name='reports'),
    path('reports/create/', views.create_report, name='create_report'),
    path('reports/<int:report_id>/approve/', views.approve_report, name='approve_report'),
    path('reports/<int:report_id>/reject/', views.reject_report, name='reject_report'),
]
