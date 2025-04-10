# accounting/urls.py
from django.urls import path
from .views import AccountingEntityListCreateAPIView, LedgerReportAPIView, ReportSettingListCreateAPIView

urlpatterns = [
    path('entities/', AccountingEntityListCreateAPIView.as_view(), name='list-create-entities'),
    path('report/', LedgerReportAPIView.as_view(), name='ledger-report'),
    path('report-settings/', ReportSettingListCreateAPIView.as_view(), name='list-create-report-settings'),
]
