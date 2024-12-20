from django.urls import path
from . import views

app_name = 'sector'

urlpatterns = [
    # Sektor əməliyyatları
    path('', views.sector_list, name='sector_list'),
    path('<int:pk>/', views.sector_detail, name='sector_detail'),
    path('<int:pk>/documents/', views.sector_documents, name='sector_documents'),
    path('<int:pk>/news/', views.sector_news, name='sector_news'),
    path('<int:pk>/statistics/', views.sector_statistics, name='sector_statistics'),
    
    # Hesabat əməliyyatları
    path('<int:pk>/reports/', views.sector_reports, name='sector_reports'),
    path('<int:pk>/reports/create/', views.report_create, name='report_create'),
    path('reports/<int:report_pk>/', views.report_detail, name='report_detail'),
    path('reports/<int:report_pk>/edit/', views.report_edit, name='report_edit'),
    path('reports/<int:report_pk>/approve/', views.report_approve, name='report_approve'),
    path('reports/<int:report_pk>/reject/', views.report_reject, name='report_reject'),
    
    # Xəbər əməliyyatları
    path('<int:pk>/news/create/', views.news_create, name='news_create'),
    path('news/<int:news_pk>/edit/', views.news_edit, name='news_edit'),
    path('news/<int:news_pk>/delete/', views.news_delete, name='news_delete'),
    path('news/<int:news_pk>/toggle-status/', views.news_toggle_status, name='news_toggle_status'),
    path('news/<int:news_pk>/details/', views.news_details, name='news_details'),
    
    # Sənəd əməliyyatları
    path('<int:pk>/documents/upload/', views.document_upload, name='document_upload'),
    path('documents/<int:doc_pk>/delete/', views.document_delete, name='document_delete'),
    path('documents/<int:doc_pk>/details/', views.document_details, name='document_details'),
]
