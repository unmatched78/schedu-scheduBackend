# # payroll_benefits/views.py
# from rest_framework import generics, status
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from django.core.exceptions import PermissionDenied
# from django.shortcuts import get_object_or_404
# from .models import Benefit, WorkerBenefit, PayrollSettings, Payroll
# from .serializers import BenefitSerializer, WorkerBenefitSerializer, PayrollSettingsSerializer, PayrollSerializer
# from rolepermissions.checkers import has_permission
# from core.models import Worker, CustomUser
# from ticketing.utils import send_automatic_notification
# from django.utils import timezone

# class BenefitListAPIView(generics.ListAPIView):
#     serializer_class = BenefitSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return Benefit.objects.filter(organization=self.request.user.organization, is_active=True)

# class BenefitCreateUpdateAPIView(generics.RetrieveUpdateAPIView, generics.CreateAPIView):
#     queryset = Benefit.objects.all()
#     serializer_class = BenefitSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         if not has_permission(self.request.user, 'manage_organization'):
#             raise PermissionDenied("Permission denied.")
#         benefit = serializer.save(organization=self.request.user.organization)
#         send_automatic_notification(
#             users=CustomUser.objects.filter(organization=self.request.user.organization),
#             message=f"New benefit '{benefit.name}' ({benefit.benefit_type}) added by {self.request.user.username}."
#         )

#     def perform_update(self, serializer):
#         if not has_permission(self.request.user, 'manage_organization'):
#             raise PermissionDenied("Permission denied.")
#         benefit = serializer.save()
#         send_automatic_notification(
#             users=CustomUser.objects.filter(organization=self.request.user.organization),
#             message=f"Benefit '{benefit.name}' updated by {self.request.user.username}."
#         )

# class WorkerBenefitEnrollAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         benefit_id = request.data.get('benefit_id')
#         contribution_amount = request.data.get('contribution_amount')
#         period = request.data.get('period')
        
#         benefit = get_object_or_404(Benefit, id=benefit_id, organization=request.user.organization)
#         if benefit.enrollment_start and benefit.enrollment_end:
#             today = timezone.now().date()
#             if not (benefit.enrollment_start <= today <= benefit.enrollment_end):
#                 return Response({"error": "Enrollment period is closed."}, status=400)
        
#         worker_benefit = WorkerBenefit.objects.create(
#             worker=request.user.worker_profile,
#             benefit=benefit,
#             contribution_amount=contribution_amount,
#             deduction_period=period
#         )
#         send_automatic_notification(
#             users=[request.user],
#             message=f"You have enrolled in {benefit.name} for {period} with a contribution of ${contribution_amount}."
#         )
#         return Response(WorkerBenefitSerializer(worker_benefit).data, status=201)

# class PayrollSettingsCreateAPIView(generics.CreateAPIView):
#     queryset = PayrollSettings.objects.all()
#     serializer_class = PayrollSettingsSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         if not has_permission(self.request.user, 'manage_organization'):
#             raise PermissionDenied("Permission denied.")
#         settings = serializer.save()
#         send_automatic_notification(
#             users=[settings.worker.user],
#             message=f"Your payroll settings have been updated by {self.request.user.username}: Base Salary ${settings.base_salary}."
#         )

# class PayrollGenerateAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         if not has_permission(request.user, 'manage_organization'):
#             return Response({"error": "Permission denied."}, status=403)
#         period = request.data.get('period')
#         workers = Worker.objects.filter(department__organization=request.user.organization)
#         for worker in workers:
#             settings = getattr(worker, 'payroll_settings', None)
#             if not settings:
#                 return Response({"error": f"No payroll settings for {worker.user.username}."}, status=400)
#             payroll = Payroll.objects.create(
#                 worker=worker,
#                 period=period,
#                 base_salary=settings.base_salary,
#                 bonuses=settings.default_bonuses,
#                 breakdown=settings.default_deductions.copy()
#             )
#             send_automatic_notification(
#                 users=[worker.user],
#                 message=f"Your payroll for {period} has been generated: Total ${payroll.total}."
#             )
#         return Response({"success": f"Payroll generated for {period}."}, status=201)

# class PayrollListAPIView(generics.ListAPIView):
#     serializer_class = PayrollSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return Payroll.objects.filter(worker=self.request.user.worker_profile)
# payroll_benefits/views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Benefit, WorkerBenefit, PayrollSettings, Payroll
from .serializers import BenefitSerializer, WorkerBenefitSerializer, PayrollSettingsSerializer, PayrollSerializer
from core.permissions import require_permission, has_permission
from core.models import Worker, CustomUser
from ticketing.utils import send_automatic_notification
from django.utils import timezone

class BenefitListAPIView(generics.ListAPIView):
    serializer_class = BenefitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if has_permission(self.request.user, 'view_benefits'):
            return Benefit.objects.filter(organization=self.request.user.organization, is_active=True)
        return Benefit.objects.none()

class BenefitCreateUpdateAPIView(generics.RetrieveUpdateAPIView, generics.CreateAPIView):
    queryset = Benefit.objects.all()
    serializer_class = BenefitSerializer
    permission_classes = [IsAuthenticated]

    @require_permission('create_benefits')
    def perform_create(self, serializer):
        benefit = serializer.save(organization=self.request.user.organization)
        send_automatic_notification(
            users=CustomUser.objects.filter(organization=self.request.user.organization),
            message=f"New benefit '{benefit.name}' ({benefit.benefit_type}) added by {self.request.user.username}."
        )

    @require_permission('edit_benefits')
    def perform_update(self, serializer):
        benefit = serializer.save()
        send_automatic_notification(
            users=CustomUser.objects.filter(organization=self.request.user.organization),
            message=f"Benefit '{benefit.name}' updated by {self.request.user.username}."
        )

class WorkerBenefitEnrollAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @require_permission('enroll_in_benefits')
    def post(self, request):
        benefit_id = request.data.get('benefit_id')
        contribution_amount = request.data.get('contribution_amount')
        period = request.data.get('period')

        benefit = get_object_or_404(Benefit, id=benefit_id, organization=request.user.organization)
        if benefit.enrollment_start and benefit.enrollment_end:
            today = timezone.now().date()
            if not (benefit.enrollment_start <= today <= benefit.enrollment_end):
                return Response({"error": "Enrollment period is closed."}, status=400)

        worker_benefit = WorkerBenefit.objects.create(
            worker=request.user.worker_profile,
            benefit=benefit,
            contribution_amount=contribution_amount,
            deduction_period=period
        )
        send_automatic_notification(
            users=[request.user],
            message=f"You have enrolled in {benefit.name} for {period} with a contribution of ${contribution_amount}."
        )
        return Response(WorkerBenefitSerializer(worker_benefit).data, status=201)

class PayrollSettingsCreateAPIView(generics.CreateAPIView):
    queryset = PayrollSettings.objects.all()
    serializer_class = PayrollSettingsSerializer
    permission_classes = [IsAuthenticated]

    @require_permission('edit_payroll_settings')
    def perform_create(self, serializer):
        settings = serializer.save()
        send_automatic_notification(
            users=[settings.worker.user],
            message=f"Your payroll settings have been updated by {self.request.user.username}: Base Salary ${settings.base_salary}."
        )

class PayrollGenerateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @require_permission('generate_payroll')
    def post(self, request):
        period = request.data.get('period')
        workers = Worker.objects.filter(department__organization=request.user.organization)
        for worker in workers:
            settings = getattr(worker, 'payroll_settings', None)
            if not settings:
                return Response({"error": f"No payroll settings for {worker.user.username}."}, status=400)
            payroll = Payroll.objects.create(
                worker=worker,
                period=period,
                base_salary=settings.base_salary,
                bonuses=settings.default_bonuses,
                breakdown=settings.default_deductions.copy()
            )
            send_automatic_notification(
                users=[worker.user],
                message=f"Your payroll for {period} has been generated: Total ${payroll.total}."
            )
        return Response({"success": f"Payroll generated for {period}."}, status=201)

class PayrollListAPIView(generics.ListAPIView):
    serializer_class = PayrollSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if has_permission(self.request.user, 'view_payroll_details'):
            return Payroll.objects.filter(worker=self.request.user.worker_profile)
        return Payroll.objects.none()