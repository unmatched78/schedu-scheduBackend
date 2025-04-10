# payroll_benefits/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('benefits/', BenefitListAPIView.as_view(), name='list-benefits'),
    path('benefits/create/', BenefitCreateUpdateAPIView.as_view(), name='create-benefit'),
    path('benefits/<int:pk>/update/', BenefitCreateUpdateAPIView.as_view(), name='update-benefit'),
    path('benefits/enroll/', WorkerBenefitEnrollAPIView.as_view(), name='enroll-benefit'),
    path('payroll/settings/create/', PayrollSettingsCreateAPIView.as_view(), name='create-payroll-settings'),
    path('payroll/generate/', PayrollGenerateAPIView.as_view(), name='generate-payroll'),
    path('payroll/', PayrollListAPIView.as_view(), name='list-payroll'),
]