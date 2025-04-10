# # hr/views.py
# from rest_framework import generics, status
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from django.core.exceptions import PermissionDenied
# from .models import LeaveRequest, Payslip, CompanyPolicy, PerformanceReview, Goal
# from .serializers import LeaveRequestSerializer, PayslipSerializer, CompanyPolicySerializer, PerformanceReviewSerializer, GoalSerializer
# from rolepermissions.checkers import has_permission
# from core.models import Worker, CustomUser
# from ticketing.utils import send_automatic_notification
# #for worker
# class LeaveRequestCreateAPIView(generics.CreateAPIView):
#     queryset = LeaveRequest.objects.all()
#     serializer_class = LeaveRequestSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         leave_request = serializer.save(worker=self.request.user.worker_profile)
#         department = leave_request.worker.department
#         send_automatic_notification(
#             users=[department.head] if department and department.head else [],
#             message=f"New leave request from {self.request.user.username} for {leave_request.start_date} to {leave_request.end_date}."
#         )
# #for admin
# class LeaveRequestListAPIView(generics.ListAPIView):
#     serializer_class = LeaveRequestSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         if has_permission(user, 'manage_department'):
#             return LeaveRequest.objects.filter(worker__department=user.managed_department)
#         return LeaveRequest.objects.filter(worker=user.worker_profile)
# #for admin
# class LeaveRequestUpdateAPIView(generics.UpdateAPIView):
#     queryset = LeaveRequest.objects.all()
#     serializer_class = LeaveRequestSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_update(self, serializer):
#         if not has_permission(self.request.user, 'manage_department'):
#             raise PermissionDenied("Permission denied.")
#         leave_request = serializer.save()
#         send_automatic_notification(
#             users=[leave_request.worker.user],
#             message=f"Leave request from {leave_request.start_date} to {leave_request.end_date} has been {leave_request.status} by {self.request.user.username}."
#         )
# #for admin
# class PayslipListAPIView(generics.ListAPIView):
#     serializer_class = PayslipSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return Payslip.objects.filter(worker=self.request.user.worker_profile)
# #for admin
# class CompanyPolicyListAPIView(generics.ListAPIView):
#     serializer_class = CompanyPolicySerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         if user.organization:
#             return CompanyPolicy.objects.filter(organization=user.organization)
#         return CompanyPolicy.objects.none()
# #for admin
# class CompanyPolicyCreateAPIView(generics.CreateAPIView):
#     queryset = CompanyPolicy.objects.all()
#     serializer_class = CompanyPolicySerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         if not has_permission(self.request.user, 'manage_organization'):
#             raise PermissionDenied("Permission denied.")
#         policy = serializer.save(organization=self.request.user.organization)
#         send_automatic_notification(
#             users=CustomUser.objects.filter(organization=self.request.user.organization),
#             message=f"New company policy '{policy.title}' has been added by {self.request.user.username}."
#         )
# #for admin
# class PerformanceReviewCreateAPIView(generics.CreateAPIView):
#     queryset = PerformanceReview.objects.all()
#     serializer_class = PerformanceReviewSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         if not (has_permission(self.request.user, 'manage_department') or has_permission(self.request.user, 'manage_organization')):
#             raise PermissionDenied("Permission denied.")
#         review = serializer.save(reviewer=self.request.user)
#         send_automatic_notification(
#             users=[review.worker.user],
#             message=f"You have a new performance review from {self.request.user.username} with score {review.score}."
#         )
# #for admin
# class PerformanceReviewListAPIView(generics.ListAPIView):
#     serializer_class = PerformanceReviewSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return PerformanceReview.objects.filter(worker=self.request.user.worker_profile)
# #for worker
# class GoalCreateAPIView(generics.CreateAPIView):
#     queryset = Goal.objects.all()
#     serializer_class = GoalSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         goal = serializer.save(worker=self.request.user.worker_profile)
#         department = goal.worker.department
#         if department and department.head:
#             send_automatic_notification(
#                 users=[department.head],
#                 message=f"{self.request.user.username} has set a new goal: '{goal.description}' due by {goal.deadline}."
#             )
# #for worker
# class GoalListAPIView(generics.ListAPIView):
#     serializer_class = GoalSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return Goal.objects.filter(worker=self.request.user.worker_profile)
# hr/views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import PermissionDenied
from .models import LeaveRequest, Payslip, CompanyPolicy, PerformanceReview, Goal
from .serializers import LeaveRequestSerializer, PayslipSerializer, CompanyPolicySerializer, PerformanceReviewSerializer, GoalSerializer
from core.permissions import require_permission, require_any_permission, has_permission
from core.models import Worker, CustomUser
from ticketing.utils import send_automatic_notification

# For worker
class LeaveRequestCreateAPIView(generics.CreateAPIView):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    @require_permission('create_leave_requests')
    def perform_create(self, serializer):
        leave_request = serializer.save(worker=self.request.user.worker_profile)
        department = leave_request.worker.department
        send_automatic_notification(
            users=[department.head] if department and department.head else [],
            message=f"New leave request from {self.request.user.username} for {leave_request.start_date} to {leave_request.end_date}."
        )

# For admin/department head
class LeaveRequestListAPIView(generics.ListAPIView):
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if has_permission(user, 'view_all_leave_requests'):
            return LeaveRequest.objects.filter(worker__department=user.managed_department)
        return LeaveRequest.objects.filter(worker=user.worker_profile)

# For admin/department head
class LeaveRequestUpdateAPIView(generics.UpdateAPIView):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    @require_permission('approve_leave_requests')
    def perform_update(self, serializer):
        leave_request = serializer.save()
        send_automatic_notification(
            users=[leave_request.worker.user],
            message=f"Leave request from {leave_request.start_date} to {leave_request.end_date} has been {leave_request.status} by {self.request.user.username}."
        )

# For worker
class PayslipListAPIView(generics.ListAPIView):
    serializer_class = PayslipSerializer
    permission_classes = [IsAuthenticated]

    @require_permission('view_payslips')
    def get_queryset(self):
        return Payslip.objects.filter(worker=self.request.user.worker_profile)

# For all users
class CompanyPolicyListAPIView(generics.ListAPIView):
    serializer_class = CompanyPolicySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if has_permission(user, 'view_company_policies') and user.organization:
            return CompanyPolicy.objects.filter(organization=user.organization)
        return CompanyPolicy.objects.none()

# For admin
class CompanyPolicyCreateAPIView(generics.CreateAPIView):
    queryset = CompanyPolicy.objects.all()
    serializer_class = CompanyPolicySerializer
    permission_classes = [IsAuthenticated]

    @require_permission('create_company_policies')
    def perform_create(self, serializer):
        policy = serializer.save(organization=self.request.user.organization)
        send_automatic_notification(
            users=CustomUser.objects.filter(organization=self.request.user.organization),
            message=f"New company policy '{policy.title}' has been added by {self.request.user.username}."
        )

# For admin/department head
class PerformanceReviewCreateAPIView(generics.CreateAPIView):
    queryset = PerformanceReview.objects.all()
    serializer_class = PerformanceReviewSerializer
    permission_classes = [IsAuthenticated]

    @require_any_permission(['create_performance_reviews', 'manage_organization'])
    def perform_create(self, serializer):
        review = serializer.save(reviewer=self.request.user)
        send_automatic_notification(
            users=[review.worker.user],
            message=f"You have a new performance review from {self.request.user.username} with score {review.score}."
        )

# For worker
class PerformanceReviewListAPIView(generics.ListAPIView):
    serializer_class = PerformanceReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if has_permission(self.request.user, 'view_performance_reviews'):
            return PerformanceReview.objects.filter(worker=self.request.user.worker_profile)
        return PerformanceReview.objects.none()

# For worker
class GoalCreateAPIView(generics.CreateAPIView):
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]

    @require_permission('create_goals')
    def perform_create(self, serializer):
        goal = serializer.save(worker=self.request.user.worker_profile)
        department = goal.worker.department
        if department and department.head:
            send_automatic_notification(
                users=[department.head],
                message=f"{self.request.user.username} has set a new goal: '{goal.description}' due by {goal.deadline}."
            )

# For worker
class GoalListAPIView(generics.ListAPIView):
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if has_permission(self.request.user, 'view_goals'):
            return Goal.objects.filter(worker=self.request.user.worker_profile)
        return Goal.objects.none()