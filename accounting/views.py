# # accounting/views.py
# from rest_framework import generics, status
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from django.core.exceptions import PermissionDenied
# from .models import AccountingEntity, ReportSetting
# from django_ledger.models import JournalEntryModel
# from .serializers import AccountingEntitySerializer, ReportSettingSerializer
# from rolepermissions.checkers import has_permission
# from core.models import CustomUser
# from ticketing.utils import send_automatic_notification
# from django.utils import timezone
# from rest_framework import serializers
# from datetime import datetime

# class AccountingEntitySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = AccountingEntity
#         fields = ['id', 'organization', 'name', 'slug', 'created', 'updated']

# class AccountingEntityListCreateAPIView(generics.ListCreateAPIView):
#     serializer_class = AccountingEntitySerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return AccountingEntity.objects.filter(organization=self.request.user.organization)

#     def perform_create(self, serializer):
#         if not has_permission(self.request.user, 'manage_organization'):
#             raise PermissionDenied("Permission denied.")
#         entity = serializer.save(organization=self.request.user.organization)
#         send_automatic_notification(
#             users=CustomUser.objects.filter(organization=self.request.user.organization, rolepermissions__permission='manage_organization'),
#             message=f"New accounting entity for {entity.organization.name} created by {self.request.user.username}."
#         )

# class LedgerReportAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         if not has_permission(request.user, 'manage_organization'):
#             return Response({"error": "Permission denied."}, status=403)
        
#         entity = AccountingEntity.objects.get(organization=self.request.user.organization)
        
#         from_date_str = request.query_params.get('from_date')
#         to_date_str = request.query_params.get('to_date')
#         today = timezone.now().date()
#         default_from_date = today.replace(month=1, day=1)
#         default_to_date = today.replace(month=12, day=31)

#         try:
#             from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date() if from_date_str else default_from_date
#             to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date() if to_date_str else default_to_date
#         except ValueError:
#             return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

#         if from_date > to_date:
#             return Response({"error": "from_date must be earlier than to_date."}, status=400)

#         # Generate Balance Sheet and Income Statement using EntityModel methods
#         balance_sheet_data = entity.get_balance_sheet(to_date=to_date)
#         income_statement_data = entity.get_income_statement(from_date=from_date, to_date=to_date)
        
#         report = {
#             "from_date": str(from_date),
#             "to_date": str(to_date),
#             "balance_sheet": {
#                 "assets": float(balance_sheet_data['assets']),
#                 "liabilities": float(balance_sheet_data['liabilities']),
#                 "equity": float(balance_sheet_data['equity'])
#             },
#             "income_statement": {
#                 "revenue": float(income_statement_data['revenue']),
#                 "expenses": float(income_statement_data['expenses']),
#                 "net_income": float(income_statement_data['net_income'])
#             }
#         }
        
#         return Response(report, status=200)

# class ReportSettingListCreateAPIView(generics.ListCreateAPIView):
#     serializer_class = ReportSettingSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return ReportSetting.objects.filter(entity__organization=self.request.user.organization)

#     def perform_create(self, serializer):
#         if not has_permission(self.request.user, 'manage_organization'):
#             raise PermissionDenied("Permission denied.")
#         entity = AccountingEntity.objects.get(organization=self.request.user.organization)
#         setting = serializer.save(entity=entity)
#         send_automatic_notification(
#             users=CustomUser.objects.filter(organization=self.request.user.organization, rolepermissions__permission='manage_organization'),
#             message=f"New report setting '{setting.name}' ({setting.frequency}) created by {self.request.user.username}."
#         )
# accounting/views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import PermissionDenied
from .models import AccountingEntity, ReportSetting
from django_ledger.models import JournalEntryModel
from .serializers import AccountingEntitySerializer, ReportSettingSerializer
from core.permissions import require_permission, has_permission
from core.models import CustomUser
from ticketing.utils import send_automatic_notification
from django.utils import timezone
from datetime import datetime

class AccountingEntityListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AccountingEntitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if has_permission(self.request.user, 'view_accounting_entities'):
            return AccountingEntity.objects.filter(organization=self.request.user.organization)
        return AccountingEntity.objects.none()

    @require_permission('create_accounting_entities')
    def perform_create(self, serializer):
        entity = serializer.save(organization=self.request.user.organization)
        org_admins = CustomUser.objects.filter(
            organization=self.request.user.organization,
            custom_role__permissions__contains=['manage_organization']
        )
        send_automatic_notification(
            users=org_admins,
            message=f"New accounting entity for {entity.organization.name} created by {self.request.user.username}."
        )

class LedgerReportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @require_permission('generate_ledger_reports')
    def get(self, request):
        try:
            entity = AccountingEntity.objects.get(organization=self.request.user.organization)
        except AccountingEntity.DoesNotExist:
            return Response({"error": "No accounting entity found for your organization."}, status=404)

        from_date_str = request.query_params.get('from_date')
        to_date_str = request.query_params.get('to_date')
        today = timezone.now().date()
        default_from_date = today.replace(month=1, day=1)
        default_to_date = today.replace(month=12, day=31)

        try:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date() if from_date_str else default_from_date
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date() if to_date_str else default_to_date
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        if from_date > to_date:
            return Response({"error": "from_date must be earlier than to_date."}, status=400)

        # Generate Balance Sheet and Income Statement using EntityModel methods
        balance_sheet_data = entity.get_balance_sheet(to_date=to_date)
        income_statement_data = entity.get_income_statement(from_date=from_date, to_date=to_date)

        report = {
            "from_date": str(from_date),
            "to_date": str(to_date),
            "balance_sheet": {
                "assets": float(balance_sheet_data['assets']),
                "liabilities": float(balance_sheet_data['liabilities']),
                "equity": float(balance_sheet_data['equity'])
            },
            "income_statement": {
                "revenue": float(income_statement_data['revenue']),
                "expenses": float(income_statement_data['expenses']),
                "net_income": float(income_statement_data['net_income'])
            }
        }

        return Response(report, status=200)

class ReportSettingListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ReportSettingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if has_permission(self.request.user, 'view_report_settings'):
            return ReportSetting.objects.filter(entity__organization=self.request.user.organization)
        return ReportSetting.objects.none()

    @require_permission('create_report_settings')
    def perform_create(self, serializer):
        entity = AccountingEntity.objects.get(organization=self.request.user.organization)
        setting = serializer.save(entity=entity)
        org_admins = CustomUser.objects.filter(
            organization=self.request.user.organization,
            custom_role__permissions__contains=['manage_organization']
        )
        send_automatic_notification(
            users=org_admins,
            message=f"New report setting '{setting.name}' ({setting.frequency}) created by {self.request.user.username}."
        )