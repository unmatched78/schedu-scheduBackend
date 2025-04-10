# # core/views.py
# from rest_framework import status
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import AllowAny, IsAuthenticated
# from rest_framework.authtoken.models import Token
# from django.contrib.auth import authenticate, logout
# from rolepermissions.checkers import has_permission
# from .serializers import *
# from django.shortcuts import get_object_or_404
# import uuid, io, base64, qrcode
# from scheduling.models import Department
# from django.core.exceptions import PermissionDenied
# from rolepermissions.roles import assign_role, remove_role, RolesManager, get_user_roles
# from django.utils.text import camel_case_to_spaces
# from ticketing.utils import send_automatic_notification  # Import from ticketing app
# from. models import*
# import logging
# from .models import has_permission, has_role
# logger = logging.getLogger(__name__)

# class OrganizationUsersAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         if not has_permission(request.user, 'manage_organization'):
#             return Response({"error": "Permission denied."}, status=403)
#         if not request.user.organization:
#             return Response({"error": "No organization associated."}, status=400)
#         users = CustomUser.objects.filter(organization=request.user.organization)
#         serializer = UserSerializer(users, many=True)
#         return Response(serializer.data, status=200)
# class UserProfileAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         serializer = UserSerializer(user)
#         data = serializer.data
#         if hasattr(user, 'managed_department') and user.managed_department:
#             data['managed_department'] = {
#                 'id': user.managed_department.id,
#                 'name': user.managed_department.name,
#                 'workers': [
#                     {'id': w.user.id, 'username': w.user.username, 'email': w.user.email}
#                     for w in Worker.objects.filter(department=user.managed_department)
#                 ]
#             }
#         return Response(data)

# class UserRoleUpdateAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         if not has_permission(request.user, 'manage_organisation'):
#             return Response({"error": "Permission denied."}, status=403)

#         serializer = UserRoleUpdateSerializer(data=request.data)
#         if serializer.is_valid():
#             username = serializer.validated_data['username']
#             new_role = serializer.validated_data['new_role']

#             try:
#                 user = CustomUser.objects.get(username=username)
#                 current_roles = get_user_roles(user)
#                 for role in current_roles:
#                     remove_role(user, role)
                
#                 role_classes = {
#                     'MainAdmin': MainAdmin,
#                     'OrganizationAdmin': OrganizationAdmin,
#                     'DepartmentHead': DepartmentHead,
#                     'WorkerRole': WorkerRole
#                 }
#                 if new_role in role_classes:
#                     assign_role(user, role_classes[new_role])
#                 else:
#                     assign_role(user, RolesManager.retrieve_role(new_role))
                
#                 send_automatic_notification(
#                     users=[user],
#                     message=f"Your role has been updated to {new_role} by {request.user.username}."
#                 )
#                 if new_role == 'DepartmentHead':
#                     send_automatic_notification(
#                         users=CustomUser.objects.filter(worker_profile__department=user.managed_department),
#                         message=f"{user.username} has been assigned as your new DepartmentHead."
#                     )

#                 return Response({"success": f"User {username} role updated to {new_role}."}, status=200)
#             except CustomUser.DoesNotExist:
#                 return Response({"error": "User not found."}, status=404)
#         return Response(serializer.errors, status=400)

# class UserDeleteAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         if not has_permission(request.user, 'manage_organisation'):
#             return Response({"error": "Permission denied."}, status=403)

#         serializer = UserDeleteSerializer(data=request.data)
#         if serializer.is_valid():
#             username = serializer.validated_data['username']
#             try:
#                 user = CustomUser.objects.get(username=username)
#                 dept = user.managed_department if hasattr(user, 'managed_department') else None
#                 user.delete()
#                 if dept:
#                     send_automatic_notification(
#                         users=CustomUser.objects.filter(worker_profile__department=dept),
#                         message=f"DepartmentHead {username} has been removed. A new head may be assigned soon."
#                     )
#                 return Response({"success": f"User {username} deleted."}, status=200)
#             except CustomUser.DoesNotExist:
#                 return Response({"error": "User not found."}, status=404)
#         return Response(serializer.errors, status=400)

# # core/views.py
# class CustomRoleCreateAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         if not has_permission(request.user, 'manage_organization'):
#             return Response({"error": "Permission denied."}, status=403)

#         serializer = CustomRoleSerializer(data=request.data)
#         if serializer.is_valid():
#             role_name = serializer.validated_data['role_name']
#             permissions = serializer.validated_data['permissions']
            
#             if not request.user.organization:
#                 return Response({"error": "You must be associated with an organization."}, status=400)

#             # Check if role already exists for this organization
#             if CustomRole.objects.filter(name=role_name, organization=request.user.organization).exists():
#                 return Response({"error": f"Role '{role_name}' already exists in your organization."}, status=400)

#             # Save the custom role
#             custom_role = CustomRole.objects.create(
#                 name=role_name,
#                 organization=request.user.organization,
#                 permissions=permissions,
#                 created_by=request.user
#             )

#             # Notify MainAdmins (excluding the requester)
#             all_users = CustomUser.objects.exclude(id=request.user.id)
#             users_with_role = [u for u in all_users if has_role(u, 'MainAdmin')]
#             send_automatic_notification(
#                 users=users_with_role,
#                 message=f"New custom role '{role_name}' created by {request.user.username} in {request.user.organization.name} with permissions: {', '.join(permissions)}."
#             )
#             return Response({"success": f"Custom role '{role_name}' created with permissions: {permissions}."}, status=201)
#         return Response(serializer.errors, status=400)



# class DepartmentInviteSignupAPIView(APIView):
#     permission_classes = [AllowAny]

#     def validate_invite(self, dept_id, invite_code):
#         if not dept_id or not invite_code:
#             return None, {"error": "Invalid invite link: missing department ID or code."}, status.HTTP_400_BAD_REQUEST
#         try:
#             department = get_object_or_404(Department, id=dept_id)
#             uuid.UUID(invite_code)
#             return department, None, None
#         except ValueError:
#             return None, {"error": "Invalid invite code format."}, status.HTTP_400_BAD_REQUEST
#         except Department.DoesNotExist:
#             return None, {"error": "Department not found."}, status.HTTP_404_NOT_FOUND
#     def get(self, request):
#         logger.info("Inside get method for invite signup")
#         dept_id = request.query_params.get('dept')
#         invite_code = request.query_params.get('code')
#         department, error, error_status = self.validate_invite(dept_id, invite_code)
        
#         if error:
#             logger.error(f"Invite validation failed: {error}")
#             return Response(error, status=error_status)
        
#         return Response({
#             "department_id": department.id,
#             "department_name": department.name,
#             "message": "Use this endpoint to register with the provided department."
#         }, status=status.HTTP_200_OK)
#     def post(self, request):
#         dept_id = request.query_params.get('dept')
#         invite_code = request.query_params.get('code')
#         department, error, error_status = self.validate_invite(dept_id, invite_code)
        
#         if error:
#             logger.error(f"Invite validation failed: {error}")
#             return Response(error, status=error_status)
    
#         data = request.data.copy()
#         data['department_id'] = dept_id
#         serializer = NormalUserRegistrationSerializer(data=data)
#         if serializer.is_valid():
#             user = serializer.save()
#             token, _ = Token.objects.get_or_create(user=user)
#             send_automatic_notification(
#                 users=[department.head] if department.head else [],
#                 message=f"New worker {user.username} has joined {department.name} via invite."
#             )
#             return Response({"token": token.key, "user": serializer.data}, status=status.HTTP_201_CREATED)
#         logger.error(f"Serializer errors: {serializer.errors}")
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# class DepartmentInviteLinkAPIView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request, department_id):
#         logger.info(f"User: {request.user.username}, Department ID: {department_id}")
#         try:
#             department = Department.objects.get(id=department_id)
#             logger.info(f"Department: {department.name}, Head: {department.head.username if department.head else 'None'}")

#             if department.head != request.user:
#                 logger.warning(f"Permission denied for {request.user.username} - not head of {department.name}")
#                 return Response(
#                     {"error": "Permission denied: Only the department head can generate invites."},
#                     status=status.HTTP_403_FORBIDDEN
#                 )

#             # Generate invite URL for frontend
#             invite_code = str(uuid.uuid4())
#             frontend_base_url = "http://localhost:3000"  # Replace with your frontend URL
#             invite_url = f"{frontend_base_url}/signup/invite?dept={department.id}&code={invite_code}"

#             # Generate QR code
#             qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L)
#             qr.add_data(invite_url)
#             qr.make(fit=True)
#             img = qr.make_image(fill_color="black", back_color="white")
#             buffer = io.BytesIO()
#             img.save(buffer, format="PNG")
#             qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

#             # Notify OrganizationAdmins
#             org_users = CustomUser.objects.filter(organization=department.organization)
#             users_with_permission = [u for u in org_users if has_role(u, 'MainAdmin')]
#             send_automatic_notification(
#                 users=users_with_permission,
#                 message=f"New department invite link generated for {department.name} by {request.user.username}: {invite_url}"
#             )

#             return Response({
#                 "invite_url": invite_url,
#                 "qr_code": qr_code_base64
#             }, status=status.HTTP_200_OK)
#         except Department.DoesNotExist:
#             logger.warning(f"Department {department_id} not found")
#             return Response({"error": "Department not found"}, status=status.HTTP_404_NOT_FOUND)

# class DepartmentHeadRegistrationAPIView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = DepartmentHeadRegistrationSerializer(data=request.data)
#         print("Request headers:", request.headers)  # Debug
#         if serializer.is_valid():
#             user = serializer.save()
#             token, _ = Token.objects.get_or_create(user=user)
#             # send_automatic_notification(
#             #     users=CustomUser.objects.filter(rolepermissions__permission='manage_all'),
#             #     message=f"New DepartmentHead {user.username} has registered."
#             # )
#              # Get users with MainAdmin role
#             all_users = CustomUser.objects.all()
#             users_with_role = [u for u in all_users if has_role(u, 'MainAdmin')]
#             send_automatic_notification(
#                 users=users_with_role,
#                 message=f"New DepartmentHead {user.username} has registered."
#             )
#             return Response({"token": token.key, "user": serializer.data}, status=201)
#         return Response(serializer.errors, status=400)

# class NormalUserRegistrationAPIView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = NormalUserRegistrationSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#             token, _ = Token.objects.get_or_create(user=user)
#             department = user.worker_profile.department
#             send_automatic_notification(
#                 users=[department.head] if department.head else [],
#                 message=f"New worker {user.username} has registered in {department.name}."
#             )
#             return Response({"token": token.key, "user": serializer.data}, status=201)
#         return Response(serializer.errors, status=400)

# # core/views.py
# class OrganizationAdminRegistrationAPIView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = OrganizationAdminRegistrationSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#             token, _ = Token.objects.get_or_create(user=user)
            
#             # Create default roles for the new organization
#             org = user.organization
#             # core/views.py
#             default_roles = [
#                 ('OrganizationAdmin', [
#                     'manage_organization', 'create_roles', 'edit_roles', 'delete_roles', 'assign_roles',
#                     'create_users', 'edit_users', 'delete_users', 'view_users', 'view_organization_details',
#                     'create_departments', 'edit_department', 'delete_department', 'assign_department_head',
#                     'view_all_shifts', 'generate_payroll', 'approve_payroll', 'edit_payroll_settings',
#                     'view_payroll_reports', 'create_benefits', 'edit_benefits', 'delete_benefits',
#                     'create_compliance_requirements', 'edit_compliance_requirements', 'view_compliance_reports',
#                     'create_legal_documents', 'edit_legal_documents', 'view_audit_logs',
#                     'create_spending_categories', 'create_budgets', 'approve_budgets', 'create_corporate_cards',
#                     'approve_expenses', 'view_spending_reports', 'create_accounting_entities', 'generate_ledger_reports'
#                 ]),
#                 ('DepartmentHead', [
#                     'edit_department', 'view_department_details', 'schedule_shifts', 'approve_swap',
#                     'view_department_shifts', 'create_tickets', 'edit_tickets', 'view_tickets',
#                     'approve_leave_requests', 'view_all_leave_requests', 'create_performance_reviews'
#                 ]),
#                 ('WorkerRole', [
#                     'work_shifts', 'request_swap', 'view_department_shifts', 'create_tickets',
#                     'view_tickets', 'view_notifications', 'create_leave_requests', 'view_leave_requests',
#                     'view_payslips', 'enroll_in_benefits', 'view_benefits', 'create_goals', 'view_goals',
#                     'create_expenses', 'view_expenses'
#                 ]),
#             ]
#             for name, perms in default_roles:
#                 role, created = CustomRole.objects.get_or_create(
#                     name=name,
#                     organization=org,
#                     defaults={'permissions': perms, 'created_by': user}
#                 )
#                 if name == 'OrganizationAdmin' and created:
#                     user.custom_role = role
#                     user.save()

#             return Response({"token": token.key, "user": serializer.data}, status=201)
#         return Response(serializer.errors, status=400)
# class LoginAPIView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)  # Use new serializer
#         if serializer.is_valid():
#             username = serializer.validated_data['username']
#             password = serializer.validated_data['password']
#             user = authenticate(username=username, password=password)
#             if user:
#                 token, _ = Token.objects.get_or_create(user=user)
#                 return Response({
#                     "token": token.key,
#                     "user": UserSerializer(user).data  # Return user data with roles
#                 }, status=status.HTTP_200_OK)
#             return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class LogoutAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         request.user.auth_token.delete()
#         logout(request)
#         return Response({"success": "Logged out successfully"}, status=200)

# # core/views.py
# class RoleListAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         if not request.user.organization:
#             return Response({"roles": []}, status=200)
#         roles = [role.name for role in CustomRole.objects.filter(organization=request.user.organization)]
#         return Response({"roles": roles}, status=200)
# from rest_framework import status
# from rolepermissions.roles import RolesManager, assign_role
# from .serializers import UserRoleUpdateSerializer  # Ensure this is imported

# # core/views.py
# class RoleAssignmentAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         if not (request.user.has_permission('manage_organization') or request.user.has_permission('manage_all')):
#             return Response({"error": "Permission denied."}, status=403)

#         serializer = UserRoleUpdateSerializer(data=request.data)
#         if serializer.is_valid():
#             username = serializer.validated_data['username']
#             role = serializer.validated_data['new_role']
            
#             available_roles = [r.name for r in CustomRole.objects.filter(organization=request.user.organization)]
#             if role not in available_roles:
#                 return Response({"error": f"Invalid role: '{role}' not available in your organization."}, status=400)
            
#             try:
#                 user = CustomUser.objects.get(username=username)
#                 custom_role = CustomRole.objects.get(name=role, organization=request.user.organization)
#                 user.custom_role = custom_role
#                 user.save()
                
#                 send_automatic_notification(
#                     users=[user],
#                     message=f"You have been assigned the role '{role}' by {request.user.username}."
#                 )
#                 return Response({"success": f"Role '{role}' assigned to user '{username}'."}, status=200)
#             except CustomUser.DoesNotExist:
#                 return Response({"error": "User not found."}, status=404)
#             except CustomRole.DoesNotExist:
#                 return Response({"error": f"Role '{role}' not found in your organization."}, status=404)
#         return Response(serializer.errors, status=400)
# core/views.py
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, logout
from django.core.exceptions import PermissionDenied
from .permissions import require_permission, require_any_permission, has_permission, has_role
from .serializers import *
from django.shortcuts import get_object_or_404
import uuid, io, base64, qrcode
from scheduling.models import Department
from ticketing.utils import send_automatic_notification
from .models import CustomUser, CustomRole, Worker
import logging

logger = logging.getLogger(__name__)

class OrganizationUsersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @require_permission('view_users')
    def get(self, request):
        if not request.user.organization:
            return Response({"error": "No organization associated."}, status=400)
        users = CustomUser.objects.filter(organization=request.user.organization)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=200)

class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        data = serializer.data
        if hasattr(user, 'managed_department') and user.managed_department:
            data['managed_department'] = {
                'id': user.managed_department.id,
                'name': user.managed_department.name,
                'workers': [
                    {'id': w.user.id, 'username': w.user.username, 'email': w.user.email}
                    for w in Worker.objects.filter(department=user.managed_department)
                ]
            }
        return Response(data)

class UserRoleUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @require_permission('assign_roles')
    def post(self, request):
        serializer = UserRoleUpdateSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            new_role = serializer.validated_data['new_role']

            available_roles = [r.name for r in CustomRole.objects.filter(organization=request.user.organization)]
            if new_role not in available_roles:
                return Response({"error": f"Invalid role: '{new_role}' not available in your organization."}, status=400)

            try:
                user = CustomUser.objects.get(username=username)
                custom_role = CustomRole.objects.get(name=new_role, organization=request.user.organization)
                user.custom_role = custom_role
                user.save()

                send_automatic_notification(
                    users=[user],
                    message=f"Your role has been updated to {new_role} by {request.user.username}."
                )
                if new_role == 'DepartmentHead' and hasattr(user, 'managed_department'):
                    send_automatic_notification(
                        users=CustomUser.objects.filter(worker_profile__department=user.managed_department),
                        message=f"{user.username} has been assigned as your new DepartmentHead."
                    )

                return Response({"success": f"User {username} role updated to {new_role}."}, status=200)
            except CustomUser.DoesNotExist:
                return Response({"error": "User not found."}, status=404)
            except CustomRole.DoesNotExist:
                return Response({"error": f"Role '{new_role}' not found in your organization."}, status=404)
        return Response(serializer.errors, status=400)

class UserDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @require_permission('delete_users')
    def post(self, request):
        serializer = UserDeleteSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            try:
                user = CustomUser.objects.get(username=username)
                dept = user.managed_department if hasattr(user, 'managed_department') else None
                user.delete()
                if dept:
                    send_automatic_notification(
                        users=CustomUser.objects.filter(worker_profile__department=dept),
                        message=f"DepartmentHead {username} has been removed. A new head may be assigned soon."
                    )
                return Response({"success": f"User {username} deleted."}, status=200)
            except CustomUser.DoesNotExist:
                return Response({"error": "User not found."}, status=404)
        return Response(serializer.errors, status=400)

class CustomRoleCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @require_permission('create_roles')
    def post(self, request):
        serializer = CustomRoleSerializer(data=request.data)
        if serializer.is_valid():
            role_name = serializer.validated_data['role_name']
            permissions = serializer.validated_data['permissions']

            if not request.user.organization:
                return Response({"error": "You must be associated with an organization."}, status=400)

            if CustomRole.objects.filter(name=role_name, organization=request.user.organization).exists():
                return Response({"error": f"Role '{role_name}' already exists in your organization."}, status=400)

            custom_role = CustomRole.objects.create(
                name=role_name,
                organization=request.user.organization,
                permissions=permissions,
                created_by=request.user
            )

            all_users = CustomUser.objects.exclude(id=request.user.id)
            users_with_role = [u for u in all_users if has_role(u, 'OrganizationAdmin')]
            send_automatic_notification(
                users=users_with_role,
                message=f"New custom role '{role_name}' created by {request.user.username} in {request.user.organization.name} with permissions: {', '.join(permissions)}."
            )
            return Response({"success": f"Custom role '{role_name}' created with permissions: {permissions}."}, status=201)
        return Response(serializer.errors, status=400)

class DepartmentInviteSignupAPIView(APIView):
    permission_classes = [AllowAny]

    def validate_invite(self, dept_id, invite_code):
        if not dept_id or not invite_code:
            return None, {"error": "Invalid invite link: missing department ID or code."}, status.HTTP_400_BAD_REQUEST
        try:
            department = get_object_or_404(Department, id=dept_id)
            uuid.UUID(invite_code)
            return department, None, None
        except ValueError:
            return None, {"error": "Invalid invite code format."}, status.HTTP_400_BAD_REQUEST
        except Department.DoesNotExist:
            return None, {"error": "Department not found."}, status.HTTP_404_NOT_FOUND

    def get(self, request):
        logger.info("Inside get method for invite signup")
        dept_id = request.query_params.get('dept')
        invite_code = request.query_params.get('code')
        department, error, error_status = self.validate_invite(dept_id, invite_code)

        if error:
            logger.error(f"Invite validation failed: {error}")
            return Response(error, status=error_status)

        return Response({
            "department_id": department.id,
            "department_name": department.name,
            "message": "Use this endpoint to register with the provided department."
        }, status=status.HTTP_200_OK)

    def post(self, request):
        dept_id = request.query_params.get('dept')
        invite_code = request.query_params.get('code')
        department, error, error_status = self.validate_invite(dept_id, invite_code)

        if error:
            logger.error(f"Invite validation failed: {error}")
            return Response(error, status=error_status)

        data = request.data.copy()
        data['department_id'] = dept_id
        serializer = NormalUserRegistrationSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            send_automatic_notification(
                users=[department.head] if department.head else [],
                message=f"New worker {user.username} has joined {department.name} via invite."
            )
            return Response({"token": token.key, "user": serializer.data}, status=status.HTTP_201_CREATED)
        logger.error(f"Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DepartmentInviteLinkAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @require_permission('assign_department_head')
    def get(self, request, department_id):
        logger.info(f"User: {request.user.username}, Department ID: {department_id}")
        try:
            department = Department.objects.get(id=department_id)
            if department.head != request.user:
                logger.warning(f"Permission denied for {request.user.username} - not head of {department.name}")
                return Response(
                    {"error": "Permission denied: Only the department head can generate invites."},
                    status=status.HTTP_403_FORBIDDEN
                )

            invite_code = str(uuid.uuid4())
            frontend_base_url = "http://localhost:3000"  # Replace with your frontend URL
            invite_url = f"{frontend_base_url}/signup/invite?dept={department.id}&code={invite_code}"

            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L)
            qr.add_data(invite_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

            org_users = CustomUser.objects.filter(organization=department.organization)
            users_with_role = [u for u in org_users if has_role(u, 'OrganizationAdmin')]
            send_automatic_notification(
                users=users_with_role,
                message=f"New department invite link generated for {department.name} by {request.user.username}: {invite_url}"
            )

            return Response({
                "invite_url": invite_url,
                "qr_code": qr_code_base64
            }, status=status.HTTP_200_OK)
        except Department.DoesNotExist:
            logger.warning(f"Department {department_id} not found")
            return Response({"error": "Department not found"}, status=status.HTTP_404_NOT_FOUND)

class DepartmentHeadRegistrationAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = DepartmentHeadRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            all_users = CustomUser.objects.all()
            users_with_role = [u for u in all_users if has_role(u, 'OrganizationAdmin')]
            send_automatic_notification(
                users=users_with_role,
                message=f"New DepartmentHead {user.username} has registered."
            )
            return Response({"token": token.key, "user": serializer.data}, status=201)
        return Response(serializer.errors, status=400)

class NormalUserRegistrationAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = NormalUserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            department = user.worker_profile.department
            send_automatic_notification(
                users=[department.head] if department.head else [],
                message=f"New worker {user.username} has registered in {department.name}."
            )
            return Response({"token": token.key, "user": serializer.data}, status=201)
        return Response(serializer.errors, status=400)

class OrganizationAdminRegistrationAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OrganizationAdminRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)

            org = user.organization
            default_roles = [
                ('OrganizationAdmin', [
                    'manage_organization', 'create_roles', 'edit_roles', 'delete_roles', 'assign_roles',
                    'create_users', 'edit_users', 'delete_users', 'view_users', 'view_organization_details',
                    'create_departments', 'edit_department', 'delete_department', 'assign_department_head',
                    'view_all_shifts', 'generate_payroll', 'approve_payroll', 'edit_payroll_settings',
                    'view_payroll_reports', 'create_benefits', 'edit_benefits', 'delete_benefits',
                    'create_compliance_requirements', 'edit_compliance_requirements', 'view_compliance_reports',
                    'create_legal_documents', 'edit_legal_documents', 'view_audit_logs','create_organization',
                    'create_spending_categories', 'create_budgets', 'approve_budgets', 'create_corporate_cards',
                    'approve_expenses', 'view_spending_reports', 'create_accounting_entities', 'generate_ledger_reports'
                ]),
                ('DepartmentHead', [
                    'edit_department', 'view_department_details', 'schedule_shifts', 'approve_swap',
                    'view_department_shifts', 'create_tickets', 'edit_tickets', 'view_tickets',
                    'approve_leave_requests', 'view_all_leave_requests', 'create_performance_reviews'
                ]),
                ('WorkerRole', [
                    'work_shifts', 'request_swap', 'view_department_shifts', 'create_tickets',
                    'view_tickets', 'view_notifications', 'create_leave_requests', 'view_leave_requests',
                    'view_payslips', 'enroll_in_benefits', 'view_benefits', 'create_goals', 'view_goals',
                    'create_expenses', 'view_expenses'
                ]),
            ]
            for name, perms in default_roles:
                role, created = CustomRole.objects.get_or_create(
                    name=name,
                    organization=org,
                    defaults={'permissions': perms, 'created_by': user}
                )
                if name == 'OrganizationAdmin' and created:
                    user.custom_role = role
                    user.save()

            return Response({"token": token.key, "user": serializer.data}, status=201)
        return Response(serializer.errors, status=400)

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({
                    "token": token.key,
                    "user": UserSerializer(user).data
                }, status=status.HTTP_200_OK)
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        logout(request)
        return Response({"success": "Logged out successfully"}, status=200)

class RoleListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.organization:
            return Response({"roles": []}, status=200)
        roles = [role.name for role in CustomRole.objects.filter(organization=request.user.organization)]
        return Response({"roles": roles}, status=200)

class RoleAssignmentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @require_any_permission(['assign_roles', 'manage_all'])
    def post(self, request):
        serializer = UserRoleUpdateSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            role = serializer.validated_data['new_role']

            available_roles = [r.name for r in CustomRole.objects.filter(organization=request.user.organization)]
            if role not in available_roles:
                return Response({"error": f"Invalid role: '{role}' not available in your organization."}, status=400)

            try:
                user = CustomUser.objects.get(username=username)
                custom_role = CustomRole.objects.get(name=role, organization=request.user.organization)
                user.custom_role = custom_role
                user.save()

                send_automatic_notification(
                    users=[user],
                    message=f"You have been assigned the role '{role}' by {request.user.username}."
                )
                return Response({"success": f"Role '{role}' assigned to user '{username}'."}, status=200)
            except CustomUser.DoesNotExist:
                return Response({"error": "User not found."}, status=404)
            except CustomRole.DoesNotExist:
                return Response({"error": f"Role '{role}' not found in your organization."}, status=404)
        return Response(serializer.errors, status=400)