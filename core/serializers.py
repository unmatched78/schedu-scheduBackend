from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *

from rolepermissions.roles import assign_role
from .roles import *

User = get_user_model()

# --- User Registration Serializers ---
class BaseRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'password', 
            'phone', 'organization', 'selfreport_organisation'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class DepartmentHeadRegistrationSerializer(BaseRegistrationSerializer):
    def create(self, validated_data):
        user = super().create(validated_data)
        assign_role(user, DepartmentHead)  # Pass the role class
        # assign_role(user, 'departmenthead')
        return user

# class NormalUserRegistrationSerializer(BaseRegistrationSerializer):
#     def create(self, validated_data):
#         user = super().create(validated_data)
#         # assign_role(user, 'worker')
#         assign_role(user, Worker)
#         return user
class NormalUserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    department_id = serializers.IntegerField(write_only=True, required=True)
    position = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'phone', 'organization', 'selfreport_organisation', 'department_id', 'position')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        department_id = validated_data.pop('department_id')
        position = validated_data.pop('position', '')

        # Create the user
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # Assign the Worker role to the user
        assign_role(user, WorkerRole)

        # Create the Worker profile associated with the user
        try:
            department = Department.objects.get(id=department_id)
            Worker.objects.create(user=user, department=department, position=position)
        except Department.DoesNotExist:
            raise serializers.ValidationError({'department_id': 'Invalid department ID.'})

        return user
class OrganizationAdminRegistrationSerializer(BaseRegistrationSerializer):
    def create(self, validated_data):
        user = super().create(validated_data)
        assign_role(user, OrganizationAdmin)
        # assign_role(user, 'organizationadmin')
        return user

# --- Organization Serializer ---
class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name']

# --- Department Serializer ---
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'organization', 'name', 'head']

# --- Worker Serializer ---
class WorkerSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Displays username
    class Meta:
        model = Worker
        fields = ['id', 'user', 'department', 'position']

# --- Shift Serializer ---
class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = '__all__'

#for queryin @username in editmode, ideally this also should be made asycnioloisly 
class ForpreloadingalltheworkersinthedepartmentforeasyuserwritinginethechsiftboxWorkerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username")  # Include username in response

    class Meta:
        model = Worker
        fields = ['id', 'username', 'position']
