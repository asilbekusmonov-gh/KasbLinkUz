from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from django.conf import settings
from root.settings import MEDIA_URL, MEDIA_ROOT

urlpatterns = [
                  path('', RedirectView.as_view(url='/api/schema/swagger-ui/')),
                  path('admin/', admin.site.urls),
                  path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
                  path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
                  # ← fix this
                  path('api/v1/', include('apps.urls')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
