from django.urls import path
from .views import *

urlpatterns = [
    path('register/department-head/', DepartmentHeadRegistrationAPIView.as_view(), name='register-department-head'),
    path('register/normal-user/', NormalUserRegistrationAPIView.as_view(), name='register-normal-user'),
    path('register/organization-admin/', OrganizationAdminRegistrationAPIView.as_view(), name='register-org-admin'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('assign-role/', RoleAssignmentAPIView.as_view(), name='assign-role'),
    path('organizations/', OrganizationCreateAPIView.as_view(), name='create-organization'),
    path('departments/', DepartmentCreateAPIView.as_view(), name='create-department'),
    path('departments/list/', DepartmentListAPIView.as_view(), name='list-departments'),
    path('workers/', WorkerListAPIView.as_view(), name='list-workers'),
    path('shifts/', ShiftCreateAPIView.as_view(), name='create-shift'),
    path('shifts/list/', ShiftListAPIView.as_view(), name='list-shifts'),
    path('shifts/<int:pk>/', ShiftDetailAPIView.as_view(), name='shift-detail'),
    # New oint for department invites:
    path('department/<int:department_id>/invite/', DepartmentInviteLinkAPIView.as_view(), name='department-invite-link')
]