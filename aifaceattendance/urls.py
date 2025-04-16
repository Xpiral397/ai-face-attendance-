from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.views.generic import TemplateView

schema_view = get_schema_view(
    openapi.Info(
        title="AI Face Attendance API",
        default_version='v1',
        description="AI Face Attendance System API Documentation",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    # path('api/academic/', include('academic.urls')),
    # path('api/schedule/', include('schedule.urls')),
    # path('api/attendance/', include('attendance.urls')),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('face-login/', TemplateView.as_view(template_name='websocket_face_login.html'), name='face-login'),
    path('', TemplateView.as_view(template_name='websocket_face_login.html'), name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 