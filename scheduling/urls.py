# scheduling/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('organizations/create/', OrganizationCreateAPIView.as_view(), name='create-organization'),
    path('organizations/', OrganizationListAPIView.as_view(), name='list-organizations'),
    path('departments/create/', DepartmentCreateAPIView.as_view(), name='create-department'),
    path('departments/', DepartmentListAPIView.as_view(), name='list-departments'),
    path('shifts/create/', ShiftCreateAPIView.as_view(), name='create-shift'),
    path('shifts/', ShiftListAPIView.as_view(), name='list-shifts'),
    path('shifts/<int:pk>/update/', ShiftUpdateAPIView.as_view(), name='update-shift'),
    #path('departments/transfer/', DepartmentTransferAPIView.as_view(), name='transfer-department'),
    path('departments/<int:department_id>/delete/', DepartmentDeleteAPIView.as_view(), name='delete-department'),  # New endpoint
    path('departments/<int:department_id>/transfer/invite/', DepartmentTransferInviteAPIView.as_view(), name='transfer-invite'),  # New endpoint
    path('departments/transfer/invite/', DepartmentTransferInviteAcceptAPIView.as_view(), name='accept-transfer-invite'),  # Updated endpoint
    path('departments/shift-settings/update/', DepartmentShiftSettingsUpdateAPIView.as_view(), name='update-shift-settings'),
    path('shifts/swap/request/', ShiftSwapRequestCreateAPIView.as_view(), name='request-shift-swap'),
    path('shifts/swap/review/<int:swap_request_id>/', ShiftSwapRequestReviewAPIView.as_view(), name='review-shift-swap'),
]