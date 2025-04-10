# # core/serializers.py
# from rest_framework import serializers
# from django.contrib.auth import get_user_model
# from rolepermissions.roles import assign_role
# from .models import Worker
# from .roles import *

# User = get_user_model()

# # New serializer for user data with roles
# class UserSerializer(serializers.ModelSerializer):
#     roles = serializers.SerializerMethodField()

#     class Meta:
#         model = User
#         fields = ('id', 'username', 'email', 'phone', 'organization', 'selfreport_organisation', 'roles')

#     def get_roles(self, obj):
#         return obj.get_roles()
# class BaseRegistrationSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = ('id', 'username', 'email', 'password', 'phone', 'organization', 'selfreport_organisation')

#     def create(self, validated_data):
#         password = validated_data.pop('password')
#         user = User(**validated_data)
#         user.set_password(password)
#         user.save()
#         return user

# class DepartmentHeadRegistrationSerializer(BaseRegistrationSerializer):
#     def create(self, validated_data):
#         user = super().create(validated_data)
#         assign_role(user, DepartmentHead)
#         return user

# class NormalUserRegistrationSerializer(BaseRegistrationSerializer):
#     department_id = serializers.IntegerField(write_only=True, required=True)
#     position = serializers.CharField(write_only=True, required=False, allow_blank=True)

#     class Meta(BaseRegistrationSerializer.Meta):
#         fields = BaseRegistrationSerializer.Meta.fields + ('department_id', 'position')

#     def create(self, validated_data):
#         department_id = validated_data.pop('department_id')
#         position = validated_data.pop('position', '')
#         user = super().create(validated_data)
#         assign_role(user, WorkerRole)
#         from scheduling.models import Department
#         department = Department.objects.get(id=department_id)
#         Worker.objects.create(user=user, department=department, position=position)
#         return user

# class OrganizationAdminRegistrationSerializer(BaseRegistrationSerializer):
#     def create(self, validated_data):
#         user = super().create(validated_data)
#         assign_role(user, OrganizationAdmin)
#         return user

# # core/serializers.py
# from rest_framework import serializers
# from .models import CustomUser
# from scheduling.serializers import DepartmentSerializer  # If Worker is linked to Department

# class UserSerializer(serializers.ModelSerializer):
#     roles = serializers.SerializerMethodField()  # Add roles from get_roles
#     worker_profile = serializers.SerializerMethodField(read_only=True)  # Optional: include Worker data
#     from scheduling.models import Department
#     managed_department = DepartmentSerializer(read_only=True)
#     class Meta:
#         model = CustomUser
#         fields = [
#             'id', 'username', 'email', 'phone', 'roles', 'worker_profile',
#             'organization', 'selfreport_organisation', 'groups', 'user_permissions', 'managed_department'
#         ]
#         # Exclude password explicitly (not needed with explicit fields, but for clarity)
#         extra_kwargs = {'password': {'write_only': True}}

#     def get_roles(self, obj):
#         return obj.get_roles()  # Assumes CustomUser has get_roles method

#     def get_worker_profile(self, obj):
#         try:
#             from .models import Worker
#             worker = Worker.objects.get(user=obj)
#             return {
#                 'department': DepartmentSerializer(worker.department).data if worker.department else None,
#                 'position': worker.position
#             }
#         except Worker.DoesNotExist:
#             return None

# # New serializer for login validation
# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField(required=True)
#     password = serializers.CharField(required=True, write_only=True)
# #=========#

# from rolepermissions.roles import assign_role, remove_role, get_user_roles
# from rolepermissions.permissions import grant_permission, revoke_permission

# class UserRoleUpdateSerializer(serializers.Serializer):
#     username = serializers.CharField(required=True)
#     new_role = serializers.CharField(required=True)  # e.g., "WorkerRole", "DepartmentHead"

#     def validate_new_role(self, value):
#         from core import roles
#         role_classes = {
#             'MainAdmin': roles.MainAdmin,
#             'OrganizationAdmin': roles.OrganizationAdmin,
#             'DepartmentHead': roles.DepartmentHead,
#             'WorkerRole': roles.WorkerRole
#         }
#         # Add custom roles dynamically later
#         if value not in role_classes and not hasattr(roles, value):
#             raise serializers.ValidationError("Invalid role name.")
#         return value

# class UserDeleteSerializer(serializers.Serializer):
#     username = serializers.CharField(required=True)

# class CustomRoleSerializer(serializers.Serializer):
#     role_name = serializers.CharField(required=True, max_length=50)
#     permissions = serializers.ListField(child=serializers.CharField(), required=True)

#     def validate_role_name(self, value):
#         from core import roles
#         if hasattr(roles, value):
#             raise serializers.ValidationError("Role name already exists.")
#         if not value.isalnum():
#             raise serializers.ValidationError("Role name must be alphanumeric.")
#         return value

#     def validate_permissions(self, value):
#         for perm in value:
#             if not perm.isalnum():
#                 raise serializers.ValidationError("Permissions must be alphanumeric.")
#         return value
# core/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import CustomUser, CustomRole, Worker
from scheduling.serializers import DepartmentSerializer
from core.permissions import AVAILABLE_PERMISSIONS

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    worker_profile = serializers.SerializerMethodField(read_only=True)
    managed_department = DepartmentSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'phone', 'roles', 'worker_profile',
            'organization', 'selfreport_organisation', 'groups', 'user_permissions', 'managed_department'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def get_roles(self, obj):
        return obj.get_roles()

    def get_worker_profile(self, obj):
        try:
            worker = Worker.objects.get(user=obj)
            return {
                'department': DepartmentSerializer(worker.department).data if worker.department else None,
                'position': worker.position
            }
        except Worker.DoesNotExist:
            return None

class BaseRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password', 'phone', 'organization', 'selfreport_organisation')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

class DepartmentHeadRegistrationSerializer(BaseRegistrationSerializer):
    def create(self, validated_data):
        user = super().create(validated_data)
        if user.organization:
            role, _ = CustomRole.objects.get_or_create(
                name='DepartmentHead',
                organization=user.organization,
                defaults={'permissions': [
                    'edit_department', 'view_department_details', 'schedule_shifts', 'approve_swap',
                    'view_department_shifts', 'create_tickets', 'edit_tickets', 'view_tickets',
                    'approve_leave_requests', 'view_all_leave_requests', 'create_performance_reviews'
                ], 'created_by': user}
            )
            user.custom_role = role
            user.save()
        return user

class NormalUserRegistrationSerializer(BaseRegistrationSerializer):
    department_id = serializers.IntegerField(write_only=True, required=True)
    position = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta(BaseRegistrationSerializer.Meta):
        fields = BaseRegistrationSerializer.Meta.fields + ('department_id', 'position')

    def create(self, validated_data):
        department_id = validated_data.pop('department_id')
        position = validated_data.pop('position', '')
        user = super().create(validated_data)
        from scheduling.models import Department
        department = Department.objects.get(id=department_id)
        if department.organization:
            role, _ = CustomRole.objects.get_or_create(
                name='WorkerRole',
                organization=department.organization,
                defaults={'permissions': [
                    'work_shifts', 'request_swap', 'view_department_shifts', 'create_tickets',
                    'view_tickets', 'view_notifications', 'create_leave_requests', 'view_leave_requests',
                    'view_payslips', 'enroll_in_benefits', 'view_benefits', 'create_goals', 'view_goals',
                    'create_expenses', 'view_expenses'
                ], 'created_by': user}
            )
            user.custom_role = role
            Worker.objects.create(user=user, department=department, position=position)
            user.save()
        return user

class OrganizationAdminRegistrationSerializer(BaseRegistrationSerializer):
    def create(self, validated_data):
        user = super().create(validated_data)
        if user.organization:
            role, _ = CustomRole.objects.get_or_create(
                name='OrganizationAdmin',
                organization=user.organization,
                defaults={'permissions': [
                    'manage_organization', 'create_roles', 'edit_roles', 'delete_roles', 'assign_roles',
                    'create_users', 'edit_users', 'delete_users', 'view_users', 'view_organization_details',
                    'create_departments', 'edit_department', 'delete_department', 'assign_department_head',
                    'view_all_shifts', 'generate_payroll', 'approve_payroll', 'edit_payroll_settings',
                    'view_payroll_reports', 'create_benefits', 'edit_benefits', 'delete_benefits',
                    'create_compliance_requirements', 'edit_compliance_requirements', 'view_compliance_reports',
                    'create_legal_documents', 'edit_legal_documents', 'view_audit_logs',
                    'create_spending_categories', 'create_budgets', 'approve_budgets', 'create_corporate_cards',
                    'approve_expenses', 'view_spending_reports', 'create_accounting_entities', 'generate_ledger_reports'
                ], 'created_by': user}
            )
            user.custom_role = role
            user.save()
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

class UserRoleUpdateSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    new_role = serializers.CharField(required=True)

    def validate_new_role(self, value):
        user = self.context['request'].user
        if not user.organization:
            raise serializers.ValidationError("User must be associated with an organization.")
        available_roles = [r.name for r in CustomRole.objects.filter(organization=user.organization)]
        if value not in available_roles:
            raise serializers.ValidationError(f"Invalid role: '{value}' not available in your organization.")
        return value

class UserDeleteSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)

class CustomRoleSerializer(serializers.Serializer):
    role_name = serializers.CharField(required=True, max_length=50)
    permissions = serializers.ListField(child=serializers.CharField(), required=True)

    def validate_role_name(self, value):
        if not value.isalnum():
            raise serializers.ValidationError("Role name must be alphanumeric.")
        return value

    def validate_permissions(self, value):
        invalid_perms = [p for p in value if p not in AVAILABLE_PERMISSIONS]
        if invalid_perms:
            raise serializers.ValidationError(f"Invalid permissions: {invalid_perms}. Must be from {AVAILABLE_PERMISSIONS}")
        return value