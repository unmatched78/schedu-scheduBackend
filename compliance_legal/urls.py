# compliance_legal/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('requirements/', ComplianceRequirementListCreateAPIView.as_view(), name='list-create-requirements'),
    path('requirements/<int:pk>/update/', ComplianceRequirementUpdateAPIView.as_view(), name='update-requirement'),
    path('documents/', LegalDocumentListCreateAPIView.as_view(), name='list-create-documents'),
    path('documents/<int:pk>/update/', LegalDocumentUpdateAPIView.as_view(), name='update-document'),
    path('audit-logs/', AuditLogListAPIView.as_view(), name='list-audit-logs'),
    path('check/', ComplianceCheckAPIView.as_view(), name='compliance-check'),
]