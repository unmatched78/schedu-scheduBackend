# # hr/urls.py
# from django.urls import path
# from .views import *

# urlpatterns = [
#     path('leave-requests/create/', LeaveRequestCreateAPIView.as_view(), name='create-leave-request'),
#     path('leave-requests/', LeaveRequestListAPIView.as_view(), name='list-leave-requests'),
#     path('leave-requests/<int:pk>/update/', LeaveRequestUpdateAPIView.as_view(), name='update-leave-request'),
#     path('payslips/', PayslipListAPIView.as_view(), name='list-payslips'),
#     path('policies/', CompanyPolicyListAPIView.as_view(), name='list-policies'),
#     path('policies/create/', CompanyPolicyCreateAPIView.as_view(), name='create-policy'),
#     path('performance-reviews/create/', PerformanceReviewCreateAPIView.as_view(), name='create-performance-review'),
#     path('performance-reviews/', PerformanceReviewListAPIView.as_view(), name='list-performance-reviews'),
#     path('goals/create/', GoalCreateAPIView.as_view(), name='create-goal'),
#     path('goals/', GoalListAPIView.as_view(), name='list-goals'),
#     path('payroll/generate/', PayrollGenerateAPIView.as_view(), name='generate-payroll'),
#     path('payroll/', PayrollListAPIView.as_view(), name='list-payroll'),
# ]
# hr/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('leave-requests/create/', LeaveRequestCreateAPIView.as_view(), name='create-leave-request'),
    path('leave-requests/', LeaveRequestListAPIView.as_view(), name='list-leave-requests'),
    path('leave-requests/<int:pk>/update/', LeaveRequestUpdateAPIView.as_view(), name='update-leave-request'),
    path('payslips/', PayslipListAPIView.as_view(), name='list-payslips'),
    path('policies/', CompanyPolicyListAPIView.as_view(), name='list-policies'),
    path('policies/create/', CompanyPolicyCreateAPIView.as_view(), name='create-policy'),
    path('reviews/create/', PerformanceReviewCreateAPIView.as_view(), name='create-review'),
    path('reviews/', PerformanceReviewListAPIView.as_view(), name='list-reviews'),
    path('goals/create/', GoalCreateAPIView.as_view(), name='create-goal'),
    path('goals/', GoalListAPIView.as_view(), name='list-goals'),
]