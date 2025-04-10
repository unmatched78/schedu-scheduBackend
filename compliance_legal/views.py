# # compliance_legal/views.py
# from rest_framework import generics, status
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from django.core.exceptions import PermissionDenied
# from django.shortcuts import get_object_or_404
# from .models import ComplianceRequirement, LegalDocument, AuditLog
# from .serializers import ComplianceRequirementSerializer, LegalDocumentSerializer, AuditLogSerializer
# from rolepermissions.checkers import has_permission
# from core.models import Worker, CustomUser
# from ticketing.utils import send_automatic_notification
# from django.utils import timezone

# class ComplianceRequirementListCreateAPIView(generics.ListCreateAPIView):
#     serializer_class = ComplianceRequirementSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         if has_permission(user, 'manage_organization'):
#             return ComplianceRequirement.objects.filter(organization=user.organization)
#         elif has_permission(user, 'manage_department'):
#             return ComplianceRequirement.objects.filter(organization=user.organization, assigned_to__department=user.managed_department)
#         return ComplianceRequirement.objects.filter(assigned_to=self.request.user.worker_profile)

#     def perform_create(self, serializer):
#         if not has_permission(self.request.user, 'manage_organization'):
#             raise PermissionDenied("Permission denied.")
#         requirement = serializer.save(organization=self.request.user.organization)
#         if requirement.assigned_to:
#             send_automatic_notification(
#                 users=[requirement.assigned_to.user],
#                 message=f"You’ve been assigned a new compliance task: '{requirement.name}' due by {requirement.due_date}."
#             )
#         send_automatic_notification(
#             users=CustomUser.objects.filter(organization=self.request.user.organization, rolepermissions__permission='manage_organization'),
#             message=f"New compliance requirement '{requirement.name}' created by {self.request.user.username}."
#         )
#         AuditLog.objects.create(
#             organization=self.request.user.organization,
#             action_type='create',
#             entity_type='ComplianceRequirement',
#             entity_id=requirement.id,
#             details=f"Created by {self.request.user.username}",
#             performed_by=self.request.user
#         )

# class ComplianceRequirementUpdateAPIView(generics.UpdateAPIView):
#     queryset = ComplianceRequirement.objects.all()
#     serializer_class = ComplianceRequirementSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_update(self, serializer):
#         if not (has_permission(self.request.user, 'manage_organization') or 
#                 (has_permission(self.request.user, 'manage_department') and 
#                  self.get_object().assigned_to.department == self.request.user.managed_department)):
#             raise PermissionDenied("Permission denied.")
#         requirement = serializer.save()
#         if requirement.status in ['compliant', 'non_compliant', 'expired']:
#             send_automatic_notification(
#                 users=[requirement.assigned_to.user] if requirement.assigned_to else [],
#                 message=f"Your compliance task '{requirement.name}' status updated to {requirement.status} by {self.request.user.username}."
#             )
#         AuditLog.objects.create(
#             organization=self.request.user.organization,
#             action_type='update',
#             entity_type='ComplianceRequirement',
#             entity_id=requirement.id,
#             details=f"Status updated to {requirement.status} by {self.request.user.username}",
#             performed_by=self.request.user
#         )

# class LegalDocumentListCreateAPIView(generics.ListCreateAPIView):
#     serializer_class = LegalDocumentSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return LegalDocument.objects.filter(organization=self.request.user.organization)

#     def perform_create(self, serializer):
#         if not has_permission(self.request.user, 'manage_organization'):
#             raise PermissionDenied("Permission denied.")
#         document = serializer.save(organization=self.request.user.organization, created_by=self.request.user)
#         send_automatic_notification(
#             users=CustomUser.objects.filter(organization=self.request.user.organization),
#             message=f"New legal document '{document.title}' ({document.document_type}) uploaded by {self.request.user.username}."
#         )
#         AuditLog.objects.create(
#             organization=self.request.user.organization,
#             action_type='create',
#             entity_type='LegalDocument',
#             entity_id=document.id,
#             details=f"Uploaded by {self.request.user.username}",
#             performed_by=self.request.user
#         )

# class LegalDocumentUpdateAPIView(generics.UpdateAPIView):
#     queryset = LegalDocument.objects.all()
#     serializer_class = LegalDocumentSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_update(self, serializer):
#         if not has_permission(self.request.user, 'manage_organization'):
#             raise PermissionDenied("Permission denied.")
#         document = serializer.save()
#         send_automatic_notification(
#             users=CustomUser.objects.filter(organization=self.request.user.organization),
#             message=f"Legal document '{document.title}' updated by {self.request.user.username}."
#         )
#         AuditLog.objects.create(
#             organization=self.request.user.organization,
#             action_type='update',
#             entity_type='LegalDocument',
#             entity_id=document.id,
#             details=f"Updated by {self.request.user.username}",
#             performed_by=self.request.user
#         )

# class AuditLogListAPIView(generics.ListAPIView):
#     serializer_class = AuditLogSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         if not has_permission(user, 'manage_organization'):
#             raise PermissionDenied("Permission denied.")
#         return AuditLog.objects.filter(organization=user.organization)

# class ComplianceCheckAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         if not has_permission(request.user, 'manage_organization'):
#             return Response({"error": "Permission denied."}, status=403)
#         today = timezone.now().date()
#         expired = ComplianceRequirement.objects.filter(
#             organization=request.user.organization,
#             due_date__lt=today,
#             status__in=['pending', 'non_compliant']
#         )
#         upcoming = ComplianceRequirement.objects.filter(
#             organization=request.user.organization,
#             due_date__gte=today,
#             due_date__lte=today + timezone.timedelta(days=30),
#             status='pending'
#         )
#         if expired.exists():
#             send_automatic_notification(
#                 users=CustomUser.objects.filter(organization=request.user.organization, rolepermissions__permission='manage_organization'),
#                 message=f"Alert: {expired.count()} compliance requirements are overdue!"
#             )
#         if upcoming.exists():
#             for req in upcoming:
#                 send_automatic_notification(
#                     users=[req.assigned_to.user] if req.assigned_to else [],
#                     message=f"Reminder: Compliance task '{req.name}' is due by {req.due_date}."
#                 )
#         return Response({
#             "expired": ComplianceRequirementSerializer(expired, many=True).data,
#             "upcoming": ComplianceRequirementSerializer(upcoming, many=True).data
#         }, status=200)
# compliance_legal/views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import ComplianceRequirement, LegalDocument, AuditLog
from .serializers import ComplianceRequirementSerializer, LegalDocumentSerializer, AuditLogSerializer
from core.permissions import require_permission, require_any_permission, has_permission
from core.models import Worker, CustomUser
from ticketing.utils import send_automatic_notification
from django.utils import timezone

class ComplianceRequirementListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ComplianceRequirementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if has_permission(user, 'view_compliance_requirements'):
            if has_permission(user, 'manage_organization'):
                return ComplianceRequirement.objects.filter(organization=user.organization)
            elif has_permission(user, 'manage_department'):
                return ComplianceRequirement.objects.filter(organization=user.organization, assigned_to__department=user.managed_department)
            return ComplianceRequirement.objects.filter(assigned_to=user.worker_profile)
        return ComplianceRequirement.objects.none()

    @require_permission('create_compliance_requirements')
    def perform_create(self, serializer):
        requirement = serializer.save(organization=self.request.user.organization)
        if requirement.assigned_to:
            send_automatic_notification(
                users=[requirement.assigned_to.user],
                message=f"You’ve been assigned a new compliance task: '{requirement.name}' due by {requirement.due_date}."
            )
        org_admins = CustomUser.objects.filter(
            organization=self.request.user.organization,
            custom_role__permissions__contains=['manage_organization']
        )
        send_automatic_notification(
            users=org_admins,
            message=f"New compliance requirement '{requirement.name}' created by {self.request.user.username}."
        )
        AuditLog.objects.create(
            organization=self.request.user.organization,
            action_type='create',
            entity_type='ComplianceRequirement',
            entity_id=requirement.id,
            details=f"Created by {self.request.user.username}",
            performed_by=self.request.user
        )

class ComplianceRequirementUpdateAPIView(generics.UpdateAPIView):
    queryset = ComplianceRequirement.objects.all()
    serializer_class = ComplianceRequirementSerializer
    permission_classes = [IsAuthenticated]

    @require_any_permission(['update_compliance_status', 'manage_organization'])
    def perform_update(self, serializer):
        requirement = self.get_object()
        if not (has_permission(self.request.user, 'manage_organization') or 
                (has_permission(self.request.user, 'manage_department') and 
                 requirement.assigned_to.department == self.request.user.managed_department)):
            raise PermissionDenied("Permission denied.")
        requirement = serializer.save()
        if requirement.status in ['compliant', 'non_compliant', 'expired']:
            send_automatic_notification(
                users=[requirement.assigned_to.user] if requirement.assigned_to else [],
                message=f"Your compliance task '{requirement.name}' status updated to {requirement.status} by {self.request.user.username}."
            )
        AuditLog.objects.create(
            organization=self.request.user.organization,
            action_type='update',
            entity_type='ComplianceRequirement',
            entity_id=requirement.id,
            details=f"Status updated to {requirement.status} by {self.request.user.username}",
            performed_by=self.request.user
        )

class LegalDocumentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = LegalDocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if has_permission(self.request.user, 'view_legal_documents'):
            return LegalDocument.objects.filter(organization=self.request.user.organization)
        return LegalDocument.objects.none()

    @require_permission('create_legal_documents')
    def perform_create(self, serializer):
        document = serializer.save(organization=self.request.user.organization, created_by=self.request.user)
        send_automatic_notification(
            users=CustomUser.objects.filter(organization=self.request.user.organization),
            message=f"New legal document '{document.title}' ({document.document_type}) uploaded by {self.request.user.username}."
        )
        AuditLog.objects.create(
            organization=self.request.user.organization,
            action_type='create',
            entity_type='LegalDocument',
            entity_id=document.id,
            details=f"Uploaded by {self.request.user.username}",
            performed_by=self.request.user
        )

class LegalDocumentUpdateAPIView(generics.UpdateAPIView):
    queryset = LegalDocument.objects.all()
    serializer_class = LegalDocumentSerializer
    permission_classes = [IsAuthenticated]

    @require_permission('edit_legal_documents')
    def perform_update(self, serializer):
        document = serializer.save()
        send_automatic_notification(
            users=CustomUser.objects.filter(organization=self.request.user.organization),
            message=f"Legal document '{document.title}' updated by {self.request.user.username}."
        )
        AuditLog.objects.create(
            organization=self.request.user.organization,
            action_type='update',
            entity_type='LegalDocument',
            entity_id=document.id,
            details=f"Updated by {self.request.user.username}",
            performed_by=self.request.user
        )

class AuditLogListAPIView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]

    @require_permission('view_audit_logs')
    def get_queryset(self):
        return AuditLog.objects.filter(organization=self.request.user.organization)

class ComplianceCheckAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @require_permission('view_compliance_reports')
    def get(self, request):
        today = timezone.now().date()
        expired = ComplianceRequirement.objects.filter(
            organization=request.user.organization,
            due_date__lt=today,
            status__in=['pending', 'non_compliant']
        )
        upcoming = ComplianceRequirement.objects.filter(
            organization=request.user.organization,
            due_date__gte=today,
            due_date__lte=today + timezone.timedelta(days=30),
            status='pending'
        )
        if expired.exists():
            org_admins = CustomUser.objects.filter(
                organization=self.request.user.organization,
                custom_role__permissions__contains=['manage_organization']
            )
            send_automatic_notification(
                users=org_admins,
                message=f"Alert: {expired.count()} compliance requirements are overdue!"
            )
        if upcoming.exists():
            for req in upcoming:
                send_automatic_notification(
                    users=[req.assigned_to.user] if req.assigned_to else [],
                    message=f"Reminder: Compliance task '{req.name}' is due by {req.due_date}."
                )
        return Response({
            "expired": ComplianceRequirementSerializer(expired, many=True).data,
            "upcoming": ComplianceRequirementSerializer(upcoming, many=True).data
        }, status=200)