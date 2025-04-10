"""
URL configuration for schedu project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.contrib import admin
from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static
# project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/core/', include('core.urls')),
    path('api/scheduling/', include('scheduling.urls')),
    path('api/hr/', include('hr.urls')),
    path('api/ticketing/', include('ticketing.urls')),
    path('api/payroll-benefits/', include('payroll_benefits.urls')),
    path('api/compliance-legal/', include('compliance_legal.urls')),
    path('api/regulatory-updates/', include('regulatory_updates.urls')),
    path('api/spending-management/', include('spending_management.urls')),
    path('ledger/', include('django_ledger.urls', namespace='django_ledger')),
    path('api/accounting/', include('accounting.urls')),
]

# serve static files and media
# urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


