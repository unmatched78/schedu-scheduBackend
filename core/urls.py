# core/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('register/department-head/', DepartmentHeadRegistrationAPIView.as_view(), name='register-department-head'),
    path('register/normal-user/', NormalUserRegistrationAPIView.as_view(), name='register-normal-user'),
    path('register/organization-admin/', OrganizationAdminRegistrationAPIView.as_view(), name='register-org-admin'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('organization/users/', OrganizationUsersAPIView.as_view(), name='organization-users'),
    path('assign-role/', RoleAssignmentAPIView.as_view(), name='assign-role'),
     path('roles/', RoleListAPIView.as_view(), name='list-roles'),  # New endpoint
    path('department/<int:department_id>/invite/', DepartmentInviteLinkAPIView.as_view(), name='department-invite-link'),
    path('profile/', UserProfileAPIView.as_view(), name='user-profile'),
    path('register/invite/', DepartmentInviteSignupAPIView.as_view(), name='department-invite-signup'),  # New endpointn
    path('users/role/update/', UserRoleUpdateAPIView.as_view(), name='update-user-role'),
    path('users/delete/', UserDeleteAPIView.as_view(), name='delete-user'),
    path('roles/custom/create/', CustomRoleCreateAPIView.as_view(), name='create-custom-role'),
]