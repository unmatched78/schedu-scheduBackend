# # scheduling/views.py
# from rest_framework import generics, status
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from django.core.exceptions import PermissionDenied
# from .models import *
# from .serializers import *
# from django.shortcuts import get_object_or_404
# from rolepermissions.checkers import has_permission
# from ticketing.utils import send_automatic_notification  # Import from ticketing app
# import uuid, qrcode, io, base64
# from django.utils import timezone
# from rolepermissions.roles import assign_role, remove_role, RolesManager, get_user_roles
# import logging
# logger = logging.getLogger(__name__)
# class DepartmentShiftSettingsUpdateAPIView(generics.UpdateAPIView):
#     queryset = DepartmentShiftSettings.objects.all()
#     serializer_class = DepartmentShiftSettingsSerializer
#     permission_classes = [IsAuthenticated]

#     def get_object(self):
#         department = self.request.user.managed_department
#         if not department or not has_permission(self.request.user, 'manage_department'):
#             raise PermissionDenied("Permission denied.")
#         return department.shift_settings

#     def perform_update(self, serializer):
#         old_policy = self.get_object().shift_swap_policy
#         serializer.save()
#         new_policy = serializer.instance.shift_swap_policy
#         if old_policy != new_policy:
#             send_automatic_notification(
#                 users=CustomUser.objects.filter(worker_profile__department=self.request.user.managed_department),
#                 message=f"Shift swap policy updated to '{new_policy}' by {self.request.user.username}."
#             )

# class ShiftSwapRequestCreateAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         original_shift_id = request.data.get('original_shift')
#         requested_shift_id = request.data.get('requested_shift')

#         try:
#             original_shift = Shift.objects.get(id=original_shift_id, workers__user=request.user)
#             requested_shift = Shift.objects.get(id=requested_shift_id)
#             department = original_shift.department
#             settings = department.shift_settings

#             if original_shift.department != requested_shift.department:
#                 return Response({"error": "Shifts must belong to the same department."}, status=400)

#             if not has_permission(request.user, 'suggest_edit'):
#                 return Response({"error": "Permission denied."}, status=403)

#             swap_request = ShiftSwapRequest.objects.create(
#                 original_shift=original_shift,
#                 requested_shift=requested_shift,
#                 requester=request.user.worker_profile
#             )

#             if settings.shift_swap_policy == 'automatic':
#                 original_shift.workers.remove(request.user.worker_profile)
#                 requested_shift.workers.add(request.user.worker_profile)
#                 swap_request.status = 'approved'
#                 swap_request.reviewed_at = timezone.now()
#                 swap_request.reviewed_by = request.user
#                 swap_request.save()
#                 send_automatic_notification(
#                     users=[department.head] if department.head else [],
#                     message=f"Shift swap auto-approved for {request.user.username}: {original_shift.shift_type} to {requested_shift.shift_type}."
#                 )
#                 return Response({
#                     "success": "Shift swapped automatically.",
#                     "swap_request": ShiftSwapRequestSerializer(swap_request).data
#                 }, status=200)
#             else:
#                 send_automatic_notification(
#                     users=[department.head] if department.head else [],
#                     message=f"New shift swap request from {request.user.username}: {original_shift.shift_type} to {requested_shift.shift_type}."
#                 )
#                 return Response({
#                     "success": "Swap request submitted for review.",
#                     "swap_request": ShiftSwapRequestSerializer(swap_request).data
#                 }, status=201)

#         except Shift.DoesNotExist:
#             return Response({"error": "One or both shifts not found or not assigned to you."}, status=404)

# class ShiftSwapRequestReviewAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, swap_request_id):
#         try:
#             swap_request = ShiftSwapRequest.objects.get(id=swap_request_id)
#             department = swap_request.original_shift.department

#             if not has_permission(request.user, 'manage_department') or department.head != request.user:
#                 return Response({"error": "Permission denied."}, status=403)

#             if swap_request.status != 'pending':
#                 return Response({"error": "Swap request already reviewed."}, status=400)

#             action = request.data.get('action')
#             if action not in ['approve', 'deny']:
#                 return Response({"error": "Invalid action. Use 'approve' or 'deny'."}, status=400)

#             if action == 'approve':
#                 swap_request.original_shift.workers.remove(swap_request.requester)
#                 swap_request.requested_shift.workers.add(swap_request.requester)
#                 swap_request.status = 'approved'
#                 message = f"Shift swap approved for {swap_request.requester.user.username}: {swap_request.original_shift.shift_type} to {swap_request.requested_shift.shift_type}."
#             else:
#                 swap_request.status = 'denied'
#                 message = f"Shift swap denied for {swap_request.requester.user.username}: {swap_request.original_shift.shift_type} to {swap_request.requested_shift.shift_type}."

#             swap_request.reviewed_at = timezone.now()
#             swap_request.reviewed_by = request.user
#             swap_request.save()

#             send_automatic_notification(
#                 users=[swap_request.requester.user],
#                 message=message
#             )

#             return Response({
#                 "success": f"Swap request {swap_request.status}.",
#                 "swap_request": ShiftSwapRequestSerializer(swap_request).data
#             }, status=200)

#         except ShiftSwapRequest.DoesNotExist:
#             return Response({"error": "Swap request not found."}, status=404)

# class DepartmentTransferInviteAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, department_id):
#         department = get_object_or_404(Department, id=department_id)
#         if not has_permission(request.user, 'manage_department') or department.head != request.user:
#             return Response({"error": "Permission denied."}, status=403)
#         if not department.is_independent:
#             return Response({"error": "Department is already part of an organization."}, status=400)

#         invite_code = str(uuid.uuid4())
#         base_url = request.build_absolute_uri('/')[:-1]
#         invite_url = f"{base_url}/api/scheduling/departments/transfer/invite/?dept={department.id}&code={invite_code}"
        
#         qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L)
#         qr.add_data(invite_url)
#         qr.make(fit=True)
#         img = qr.make_image(fill_color="black", back_color="white")
#         buffer = io.BytesIO()
#         img.save(buffer, format="PNG")
#         qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

#         org_admins = CustomUser.objects.filter(organization__isnull=False, rolepermissions__permission='manage_organization')
#         send_automatic_notification(
#             users=org_admins,
#             message=f"New department transfer invite for {department.name}. Accept via: {invite_url}"
#         )

#         return Response({
#             "invite_url": invite_url,
#             "qr_code": qr_code_base64,
#             "message": "Share this link with an OrganizationAdmin."
#         }, status=200)

# class DepartmentTransferInviteAcceptAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         if not has_permission(request.user, 'manage_organization'):
#             return Response({"error": "Permission denied."}, status=403)

#         dept_id = request.query_params.get('dept')
#         invite_code = request.query_params.get('code')

#         if not dept_id or not invite_code:
#             return Response({"error": "Invalid invite link."}, status=400)

#         try:
#             department = get_object_or_404(Department, id=dept_id, is_independent=True)
#             uuid.UUID(invite_code)
#             if department.organization:
#                 return Response({"error": "Department is already part of an organization."}, status=400)
            
#             department.organization = request.user.organization
#             department.is_independent = False
#             department.save()

#             send_automatic_notification(
#                 users=[department.head] if department.head else [],
#                 message=f"Your department {department.name} has been transferred to {request.user.organization.name}."
#             )

#             return Response({"success": f"Department {department.name} transferred to {request.user.organization.name}."}, status=200)
#         except ValueError:
#             return Response({"error": "Invalid invite code."}, status=400)
#         except Department.DoesNotExist:
#             return Response({"error": "Department not found or not independent."}, status=404)

# class OrganizationCreateAPIView(generics.CreateAPIView):
#     queryset = Organization.objects.all()
#     serializer_class = OrganizationSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         if not has_permission(self.request.user, 'manage_organization'):
#             raise PermissionDenied("Permission denied.")
#         org = serializer.save()
#         # # Get users with MainAdmin role
#         all_users = CustomUser.objects.all()
#         users_with_role = [u for u in all_users if has_role(u, 'MainAdmin')]
#         send_automatic_notification(
#             users=users_with_role,
#             message=f"New OrganizationAdmin {user.username} has registered."
#         )

# class OrganizationListAPIView(generics.ListAPIView):
#     queryset = Organization.objects.all()
#     serializer_class = OrganizationSerializer
#     permission_classes = [IsAuthenticated]
# class DepartmentCreateAPIView(generics.CreateAPIView):
#     queryset = Department.objects.all()
#     serializer_class = DepartmentSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         user = self.request.user
#         logger.info(f"User: {user.username}, Roles: {user.roles.all() if hasattr(user, 'roles') else 'No roles'}")

#         if has_permission(user, 'manage_organization'):
#             # OrganizationAdmin creating a department
#             if not user.organization:
#                 raise PermissionDenied("You are not associated with an organization.")
#             head_username = self.request.data.get('head_username')
#             if not head_username:
#                 raise serializers.ValidationError({"head_username": "A department head is required."})
#             try:
#                 head = CustomUser.objects.get(username=head_username, organization=user.organization)
#                 if Department.objects.filter(head=head).exists():
#                     existing_dept = Department.objects.filter(head=head).first()
#                     logger.warning(f"User {head.username} already manages department: {existing_dept.name}")
#                     raise PermissionDenied(f"{head.username} already manages a department.")
#             except CustomUser.DoesNotExist:
#                 raise serializers.ValidationError({"head_username": "User not found in your organization."})
#             dept = serializer.save(organization=user.organization, head=head)
#             send_automatic_notification(
#                 users=[head],
#                 message=f"You have been assigned as head of {dept.name} by {user.username}."
#             )
#         else:
#             # Non-admin (e.g., DepartmentHead) creating a department
#             if Department.objects.filter(head=user).exists():
#                 existing_dept = Department.objects.filter(head=user).first()
#                 logger.warning(f"User {user.username} already manages department: {existing_dept.name}")
#                 raise PermissionDenied("You already manage a department.")
#             dept = serializer.save(head=user)
#             send_automatic_notification(
#                 users=[user],
#                 message=f"You have created and been assigned as head of {dept.name}."
#             )

#         logger.info(f"Created department {dept.name} with head {dept.head.username}")

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# class DepartmentDeleteAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def delete(self, request, department_id):
#         if not has_permission(request.user, 'manage_organization'):
#             raise PermissionDenied("Permission denied.")
#         department = get_object_or_404(Department, id=department_id, organization=request.user.organization)
#         dept_name = department.name
#         department.delete()
#         send_automatic_notification(
#             users=CustomUser.objects.filter(organization=request.user.organization),
#             message=f"Department '{dept_name}' has been deleted by {request.user.username}."
#         )
#         return Response({"success": f"Department '{dept_name}' deleted."}, status=200)
# class DepartmentListAPIView(generics.ListAPIView):
#     serializer_class = DepartmentSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         if has_permission(user, 'manage_all'):
#             return Department.objects.all()
#         if has_permission(user, 'manage_organization'):
#             return Department.objects.filter(organization=user.organization)
#         if has_permission(user, 'manage_department'):
#             return Department.objects.filter(head=user)
#         return Department.objects.filter(id=user.worker_profile.department.id)

# class ShiftCreateAPIView(generics.CreateAPIView):
#     queryset = Shift.objects.all()
#     serializer_class = ShiftSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         if not (has_permission(self.request.user, 'manage_department') or has_permission(self.request.user, 'manage_organization')):
#             raise PermissionDenied("Permission denied.")
#         shift = serializer.save(scheduled_by=self.request.user)
#         send_automatic_notification(
#             users=[worker.user for worker in shift.workers.all()],
#             message=f"You have been scheduled for a {shift.shift_type} shift on {shift.start_time.strftime('%Y-%m-%d %H:%M')}."
#         )

# class ShiftListAPIView(generics.ListAPIView):
#     serializer_class = ShiftSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         if has_permission(user, 'manage_all') or has_permission(user, 'manage_organization'):
#             return Shift.objects.all()
#         if has_permission(user, 'manage_department'):
#             return Shift.objects.filter(department=user.managed_department)
#         return Shift.objects.filter(workers__user=user)

# class ShiftUpdateAPIView(generics.UpdateAPIView):
#     queryset = Shift.objects.all()
#     serializer_class = ShiftSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_update(self, serializer):
#         if not (has_permission(self.request.user, 'manage_department') or has_permission(self.request.user, 'manage_organization')):
#             raise PermissionDenied("Permission denied.")
#         old_workers = set(self.get_object().workers.all())
#         shift = serializer.save()
#         new_workers = set(shift.workers.all())
        
#         added = new_workers - old_workers
#         removed = old_workers - new_workers
#         if added:
#             send_automatic_notification(
#                 users=[worker.user for worker in added],
#                 message=f"You have been added to a {shift.shift_type} shift on {shift.start_time.strftime('%Y-%m-%d %H:%M')}."
#             )
#         if removed:
#             send_automatic_notification(
#                 users=[worker.user for worker in removed],
#                 message=f"You have been removed from a {shift.shift_type} shift on {shift.start_time.strftime('%Y-%m-%d %H:%M')}."
#             )
# scheduling/views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import PermissionDenied
from .models import *
from .serializers import *
from django.shortcuts import get_object_or_404
from core.permissions import require_permission, has_permission, require_any_permission, has_role
from ticketing.utils import send_automatic_notification
import uuid, qrcode, io, base64
from django.utils import timezone
import logging
logger = logging.getLogger(__name__)

class DepartmentShiftSettingsUpdateAPIView(generics.UpdateAPIView):
    queryset = DepartmentShiftSettings.objects.all()
    serializer_class = DepartmentShiftSettingsSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        department = self.request.user.managed_department
        if not department or not has_permission(self.request.user, 'manage_department'):
            raise PermissionDenied("Permission denied.")
        return department.shift_settings

    @require_permission('edit_shift_settings')
    def perform_update(self, serializer):
        old_policy = self.get_object().shift_swap_policy
        serializer.save()
        new_policy = serializer.instance.shift_swap_policy
        if old_policy != new_policy:
            send_automatic_notification(
                users=CustomUser.objects.filter(worker_profile__department=self.request.user.managed_department),
                message=f"Shift swap policy updated to '{new_policy}' by {self.request.user.username}."
            )

class ShiftSwapRequestCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @require_permission('request_shift_swap')
    def post(self, request):
        original_shift_id = request.data.get('original_shift')
        requested_shift_id = request.data.get('requested_shift')

        try:
            original_shift = Shift.objects.get(id=original_shift_id, workers__user=request.user)
            requested_shift = Shift.objects.get(id=requested_shift_id)
            department = original_shift.department
            settings = department.shift_settings

            if original_shift.department != requested_shift.department:
                return Response({"error": "Shifts must belong to the same department."}, status=400)

            swap_request = ShiftSwapRequest.objects.create(
                original_shift=original_shift,
                requested_shift=requested_shift,
                requester=request.user.worker_profile
            )

            if settings.shift_swap_policy == 'automatic':
                original_shift.workers.remove(request.user.worker_profile)
                requested_shift.workers.add(request.user.worker_profile)
                swap_request.status = 'approved'
                swap_request.reviewed_at = timezone.now()
                swap_request.reviewed_by = request.user
                swap_request.save()
                send_automatic_notification(
                    users=[department.head] if department.head else [],
                    message=f"Shift swap auto-approved for {request.user.username}: {original_shift.shift_type} to {requested_shift.shift_type}."
                )
                return Response({
                    "success": "Shift swapped automatically.",
                    "swap_request": ShiftSwapRequestSerializer(swap_request).data
                }, status=200)
            else:
                send_automatic_notification(
                    users=[department.head] if department.head else [],
                    message=f"New shift swap request from {request.user.username}: {original_shift.shift_type} to {requested_shift.shift_type}."
                )
                return Response({
                    "success": "Swap request submitted for review.",
                    "swap_request": ShiftSwapRequestSerializer(swap_request).data
                }, status=201)

        except Shift.DoesNotExist:
            return Response({"error": "One or both shifts not found or not assigned to you."}, status=404)

class ShiftSwapRequestReviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @require_permission('review_shift_swap')
    def post(self, request, swap_request_id):
        try:
            swap_request = ShiftSwapRequest.objects.get(id=swap_request_id)
            department = swap_request.original_shift.department

            if department.head != request.user:
                return Response({"error": "Permission denied."}, status=403)

            if swap_request.status != 'pending':
                return Response({"error": "Swap request already reviewed."}, status=400)

            action = request.data.get('action')
            if action not in ['approve', 'deny']:
                return Response({"error": "Invalid action. Use 'approve' or 'deny'."}, status=400)

            if action == 'approve':
                swap_request.original_shift.workers.remove(swap_request.requester)
                swap_request.requested_shift.workers.add(swap_request.requester)
                swap_request.status = 'approved'
                message = f"Shift swap approved for {swap_request.requester.user.username}: {swap_request.original_shift.shift_type} to {swap_request.requested_shift.shift_type}."
            else:
                swap_request.status = 'denied'
                message = f"Shift swap denied for {swap_request.requester.user.username}: {swap_request.original_shift.shift_type} to {swap_request.requested_shift.shift_type}."

            swap_request.reviewed_at = timezone.now()
            swap_request.reviewed_by = request.user
            swap_request.save()

            send_automatic_notification(
                users=[swap_request.requester.user],
                message=message
            )

            return Response({
                "success": f"Swap request {swap_request.status}.",
                "swap_request": ShiftSwapRequestSerializer(swap_request).data
            }, status=200)

        except ShiftSwapRequest.DoesNotExist:
            return Response({"error": "Swap request not found."}, status=404)

class DepartmentTransferInviteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @require_permission('transfer_department')
    def get(self, request, department_id):
        department = get_object_or_404(Department, id=department_id)
        if department.head != request.user:
            return Response({"error": "Permission denied."}, status=403)
        if not department.is_independent:
            return Response({"error": "Department is already part of an organization."}, status=400)

        invite_code = str(uuid.uuid4())
        base_url = request.build_absolute_uri('/')[:-1]
        invite_url = f"{base_url}/api/scheduling/departments/transfer/invite/?dept={department.id}&code={invite_code}"
        
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L)
        qr.add_data(invite_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        org_admins = CustomUser.objects.filter(
            organization__isnull=False,
            custom_role__permissions__contains=['manage_organization']
        )
        send_automatic_notification(
            users=org_admins,
            message=f"New department transfer invite for {department.name}. Accept via: {invite_url}"
        )

        return Response({
            "invite_url": invite_url,
            "qr_code": qr_code_base64,
            "message": "Share this link with an OrganizationAdmin."
        }, status=200)

class DepartmentTransferInviteAcceptAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @require_permission('accept_department_transfer')
    def post(self, request):
        dept_id = request.query_params.get('dept')
        invite_code = request.query_params.get('code')

        if not dept_id or not invite_code:
            return Response({"error": "Invalid invite link."}, status=400)

        try:
            department = get_object_or_404(Department, id=dept_id, is_independent=True)
            uuid.UUID(invite_code)
            if department.organization:
                return Response({"error": "Department is already part of an organization."}, status=400)
            
            department.organization = request.user.organization
            department.is_independent = False
            department.save()

            send_automatic_notification(
                users=[department.head] if department.head else [],
                message=f"Your department {department.name} has been transferred to {request.user.organization.name}."
            )

            return Response({"success": f"Department {department.name} transferred to {request.user.organization.name}."}, status=200)
        except ValueError:
            return Response({"error": "Invalid invite code."}, status=400)
        except Department.DoesNotExist:
            return Response({"error": "Department not found or not independent."}, status=404)

class OrganizationCreateAPIView(generics.CreateAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]

    @require_permission('create_organization')
    def perform_create(self, serializer):
        org = serializer.save()
        main_admins = CustomUser.objects.filter(custom_role__permissions__contains=['manage_organization'])
        send_automatic_notification(
            users=main_admins,
            message=f"New Organization '{org.name}' has been registered by {self.request.user.username}."
        )

class OrganizationListAPIView(generics.ListAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if has_permission(self.request.user, 'view_organizations'):
            return Organization.objects.all()
        return Organization.objects.filter(id=self.request.user.organization.id)

class DepartmentCreateAPIView(generics.CreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        logger.info(f"User: {user.username}, Permissions: {user.custom_role.permissions if hasattr(user, 'custom_role') else 'No custom role'}")

        if has_permission(user, 'manage_organization'):
            if not user.organization:
                raise PermissionDenied("You are not associated with an organization.")
            head_username = self.request.data.get('head_username')
            if not head_username:
                raise serializers.ValidationError({"head_username": "A department head is required."})
            try:
                head = CustomUser.objects.get(username=head_username, organization=user.organization)
                if Department.objects.filter(head=head).exists():
                    existing_dept = Department.objects.filter(head=head).first()
                    logger.warning(f"User {head.username} already manages department: {existing_dept.name}")
                    raise PermissionDenied(f"{head.username} already manages a department.")
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError({"head_username": "User not found in your organization."})
            dept = serializer.save(organization=user.organization, head=head)
            send_automatic_notification(
                users=[head],
                message=f"You have been assigned as head of {dept.name} by {user.username}."
            )
        else:
            if not has_permission(user, 'create_department'):
                raise PermissionDenied("Permission denied.")
            if Department.objects.filter(head=user).exists():
                existing_dept = Department.objects.filter(head=user).first()
                logger.warning(f"User {user.username} already manages department: {existing_dept.name}")
                raise PermissionDenied("You already manage a department.")
            dept = serializer.save(head=user)
            send_automatic_notification(
                users=[user],
                message=f"You have created and been assigned as head of {dept.name}."
            )

        logger.info(f"Created department {dept.name} with head {dept.head.username}")

class DepartmentDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @require_permission('delete_department')
    def delete(self, request, department_id):
        department = get_object_or_404(Department, id=department_id, organization=request.user.organization)
        dept_name = department.name
        department.delete()
        send_automatic_notification(
            users=CustomUser.objects.filter(organization=request.user.organization),
            message=f"Department '{dept_name}' has been deleted by {request.user.username}."
        )
        return Response({"success": f"Department '{dept_name}' deleted."}, status=200)

class DepartmentListAPIView(generics.ListAPIView):
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if has_permission(user, 'view_all_departments'):
            if has_permission(user, 'manage_all'):
                return Department.objects.all()
            elif has_permission(user, 'manage_organization'):
                return Department.objects.filter(organization=user.organization)
        if has_permission(user, 'manage_department'):
            return Department.objects.filter(head=user)
        return Department.objects.filter(id=user.worker_profile.department.id)

class ShiftCreateAPIView(generics.CreateAPIView):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated]

    @require_any_permission(['create_shift', 'manage_organization'])
    def perform_create(self, serializer):
        shift = serializer.save(scheduled_by=self.request.user)
        send_automatic_notification(
            users=[worker.user for worker in shift.workers.all()],
            message=f"You have been scheduled for a {shift.shift_type} shift on {shift.start_time.strftime('%Y-%m-%d %H:%M')}."
        )

class ShiftListAPIView(generics.ListAPIView):
    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if has_permission(user, 'view_all_shifts'):
            if has_permission(user, 'manage_all') or has_permission(user, 'manage_organization'):
                return Shift.objects.all()
            elif has_permission(user, 'manage_department'):
                return Shift.objects.filter(department=user.managed_department)
        return Shift.objects.filter(workers__user=user)

class ShiftUpdateAPIView(generics.UpdateAPIView):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated]

    @require_any_permission(['edit_shift', 'manage_organization'])
    def perform_update(self, serializer):
        old_workers = set(self.get_object().workers.all())
        shift = serializer.save()
        new_workers = set(shift.workers.all())
        
        added = new_workers - old_workers
        removed = old_workers - new_workers
        if added:
            send_automatic_notification(
                users=[worker.user for worker in added],
                message=f"You have been added to a {shift.shift_type} shift on {shift.start_time.strftime('%Y-%m-%d %H:%M')}."
            )
        if removed:
            send_automatic_notification(
                users=[worker.user for worker in removed],
                message=f"You have been removed from a {shift.shift_type} shift on {shift.start_time.strftime('%Y-%m-%d %H:%M')}."
            )