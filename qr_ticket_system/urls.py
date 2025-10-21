from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/login/', RedirectView.as_view(pattern_name='tickets:home', permanent=False)),
    path('admin/', admin.site.urls),
    path('', include('tickets.urls')),
]

# Serve media in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
