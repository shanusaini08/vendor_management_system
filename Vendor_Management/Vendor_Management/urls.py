from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from apis.urls import *

schema_view = get_schema_view(
    openapi.Info(
        title="Vendor Managemenet",
        default_version='v1',
        description="Vendor Profile Management , Purchase Order Tracking and Vendor Performance Evaluation",
        terms_of_service="https://www.example.com/policies/terms/",
        contact=openapi.Contact(email="vendor@example.com"),
        license=openapi.License(name="Vendor License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('apis/', include('apis.urls')),  # Include the URLs of the 'apis' app
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]