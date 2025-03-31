from django.contrib.auth import authenticate, logout, get_user_model
from django.core.exceptions import PermissionDenied
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rolepermissions.checkers import has_permission

from .models import Organization, Department, Worker, Shift
from .serializers import (
    DepartmentHeadRegistrationSerializer,
    NormalUserRegistrationSerializer,
    OrganizationAdminRegistrationSerializer,
    OrganizationSerializer,
    DepartmentSerializer,
    WorkerSerializer,
    ShiftSerializer,
)

User = get_user_model()

# --- Registration Endpoints ---

class DepartmentHeadRegistrationAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = DepartmentHeadRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "user": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NormalUserRegistrationAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = NormalUserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "user": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrganizationAdminRegistrationAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OrganizationAdminRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "user": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- Authentication Endpoints ---

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        request.user.auth_token.delete()
        logout(request)
        return Response({"success": "Logged out successfully"}, status=status.HTTP_200_OK)


# --- Role Assignment Endpoint ---

class RoleAssignmentAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        if not (has_permission(request.user, 'manage_all') or has_permission(request.user, 'manage_organization')):
            return Response({"error": "You do not have permission to assign roles."},
                            status=status.HTTP_403_FORBIDDEN)
        username = request.data.get('username')
        role = request.data.get('role')
        if not username or not role:
            return Response({"error": "Both 'username' and 'role' are required."},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        from rolepermissions.roles import assign_role
        assign_role(user, role)
        return Response({"success": f"Role '{role}' assigned to user '{username}'."},
                        status=status.HTTP_200_OK)


# --- Organization Endpoints ---

class OrganizationCreateAPIView(generics.CreateAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def perform_create(self, serializer):
        if not has_permission(self.request.user, 'manage_organization'):
            raise PermissionDenied("You do not have permission to create an organization.")
        serializer.save()


# --- Department Endpoints ---

class DepartmentCreateAPIView(generics.CreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def perform_create(self, serializer):
        if not (has_permission(self.request.user, 'manage_organization') or
                has_permission(self.request.user, 'manage_all') or 
                has_permission(self.request.user, 'manage_department')
                ):
            
            raise PermissionDenied("You do not have permission to create a department.")
        serializer.save()


class DepartmentListAPIView(generics.ListAPIView):
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        user = self.request.user
        
        # Superadmin or user with manage_all sees all departments.
        if has_permission(user, 'manage_all'):
            return Department.objects.all()
        
        # Organization admin sees only departments in their organization.
        if has_permission(user, 'manage_organization'):
            if user.organization:
                return Department.objects.filter(organization=user.organization)
            else:
                # If the organization doesn't exist, return an empty queryset.
                return Department.objects.none()
        
        # Department head sees the department they manage.
        if hasattr(user, 'managed_department'):
            return Department.objects.filter(head=user)
        
        # Worker sees only their own department.
        try:
            return Department.objects.filter(id=user.worker_profile.department.id)
        except Exception:
            return Department.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response(
                {"message": "No organization or department created yet."},
                status=status.HTTP_200_OK
            )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

# --- Worker Endpoints ---

class WorkerListAPIView(generics.ListAPIView):
    serializer_class = WorkerSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        user = self.request.user
        if has_permission(user, 'manage_all'):
            return Worker.objects.all()
        if has_permission(user, 'manage_organization'):
            if user.organization:
                return Worker.objects.filter(organization=user.organization)
            else:
                return Worker.objects.none()
        try:
            dept = user.worker_profile.department
            return Worker.objects.filter(department=dept)
        except Exception:
            return Worker.objects.none()


# --- Shift Endpoints ---

class ShiftCreateAPIView(generics.CreateAPIView):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def perform_create(self, serializer):
        if not (has_permission(self.request.user, 'manage_department') or
                has_permission(self.request.user, 'manage_organization') or
                has_permission(self.request.user, 'manage_all')):
            raise PermissionDenied("You do not have permission to create a shift.")
        serializer.save(scheduled_by=self.request.user)


class ShiftListAPIView(generics.ListAPIView):
    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        user = self.request.user
        if has_permission(user, 'manage_all') or has_permission(user, 'manage_organization'):
            return Shift.objects.all()
        if hasattr(user, 'managed_department'):
            return Shift.objects.filter(department=user.managed_department)
        try:
            return Shift.objects.filter(department=user.worker_profile.department)
        except Exception:
            return Shift.objects.none()


class ShiftDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        if has_permission(user, 'manage_all') or has_permission(user, 'manage_organization'):
            return obj
        if hasattr(user, 'managed_department') and obj.department == user.managed_department:
            return obj
        try:
            if obj.department == user.worker_profile.department:
                return obj
        except Exception:
            pass
        raise PermissionDenied("You do not have permission to access this shift.")



import io
import uuid
import base64
import qrcode
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Department

class DepartmentInviteLinkAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, department_id):
        # Verify that the logged-in user is the head of the department.
        department = get_object_or_404(Department, id=department_id)
        if department.head != request.user:
            return Response({"error": "You do not have permission to generate an invite for this department."}, status=403)
        
        # Generate a unique invite code.
        invite_code = str(uuid.uuid4())
        
        # Build the registration URL. For example, this URL might be used by the frontend.
        base_url = request.build_absolute_uri('/')[:-1]  # Removes trailing slash.
        invite_url = f"{base_url}/register/?dept={department.id}&code={invite_code}"
        
        # Generate a QR code from the invite URL.
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L)
        qr.add_data(invite_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return Response({
            "invite_url": invite_url,
            "qr_code": qr_code_base64
        })
