"""
URL configuration for school_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('region/', include('region.urls')),
    path('sector/', include('sector.urls')),
    path('school/', include('school.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler403 = 'django.views.defaults.permission_denied'
