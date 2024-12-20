"""
URL configuration for school_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import custom_permission_denied

urlpatterns = [
    path('admin/', admin.site.urls),
    path('region/', include('region.urls')),
    path('sector/', include('sector.urls')),
    path('', include('school.urls')),  # School URLs will handle both root and login
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler403 = custom_permission_denied
