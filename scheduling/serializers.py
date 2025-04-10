# # scheduling/serializers.py
# from rest_framework import serializers
# from .models import *
# from django.contrib.auth import get_user_model
# # serializers.py
# from core.models import Worker
# User = get_user_model()

# class OrganizationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Organization
#         fields = '__all__'
# class DepartmentShiftSettingsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = DepartmentShiftSettings
#         fields = ['department', 'shift_swap_policy', 'updated_at']
#         read_only_fields = ['department', 'updated_at']

# class ShiftSwapRequestSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ShiftSwapRequest
#         fields = ['id', 'original_shift', 'requested_shift', 'requester', 'status', 'created_at', 'reviewed_at', 'reviewed_by']
# # class DepartmentSerializer(serializers.ModelSerializer):
# #     organization_name = serializers.CharField(source='organization.name', read_only=True)

# #     class Meta:
# #         model = Department
# #         fields = '__all__'
# #         extra_kwargs = {
# #             'head': {'required': False},  # Head is optional in request data
# #         }
# class DepartmentSerializer(serializers.ModelSerializer):
#     organization_name = serializers.CharField(source='organization.name', read_only=True)
#     head_username = serializers.CharField(write_only=True, required=False)

#     class Meta:
#         model = Department
#         fields = ['id', 'name', 'organization', 'organization_name', 'head', 'head_username', 'is_independent']
#         extra_kwargs = {
#             'head': {'read_only': True},  # Head is set in perform_create
#             'organization': {'read_only': True},  # Set automatically for admins
#         }

#     def validate(self, data):
#         if 'head_username' in data and not self.context['request'].user.has_permission('manage_organization'):
#             raise serializers.ValidationError("Only OrganizationAdmins can specify a head.")
#         return data


# class ShiftSerializer(serializers.ModelSerializer):
#     workers = serializers.PrimaryKeyRelatedField(
#         many=True,
#         queryset=User.objects.all(),  # Accept user IDs
#         write_only=True
#     )

#     class Meta:
#         model = Shift
#         fields = '__all__'

#     def create(self, validated_data):
#         user_list = validated_data.pop('workers', [])
#         shift = super().create(validated_data)
#         workers = Worker.objects.filter(user__in=user_list)
#         shift.workers.set(workers)
#         return shift

#     def to_representation(self, instance):
#         rep = super().to_representation(instance)
#         rep['workers'] = [worker.user.id for worker in instance.workers.all()]
#         return rep
# scheduling/serializers.py
from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model
from core.models import Worker
User = get_user_model()

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'industry', 'created_at', 'updated_at']

class DepartmentShiftSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentShiftSettings
        fields = ['department', 'shift_swap_policy', 'updated_at']
        read_only_fields = ['department', 'updated_at']

class ShiftSwapRequestSerializer(serializers.ModelSerializer):
    requester_username = serializers.CharField(source='requester.user.username', read_only=True)

    class Meta:
        model = ShiftSwapRequest
        fields = ['id', 'original_shift', 'requested_shift', 'requester', 'requester_username', 
                  'status', 'created_at', 'reviewed_at', 'reviewed_by']

class DepartmentSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    head_username = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Department
        fields = ['id', 'name', 'organization', 'organization_name', 'head', 'head_username', 'is_independent']
        extra_kwargs = {
            'head': {'read_only': True},
            'organization': {'read_only': True},
        }

    def validate(self, data):
        if 'head_username' in data and not has_permission(self.context['request'].user, 'manage_organization'):
            raise serializers.ValidationError("Only OrganizationAdmins can specify a head.")
        return data

class ShiftSerializer(serializers.ModelSerializer):
    workers = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Worker.objects.all(),  # Changed to Worker objects
        write_only=True
    )
    worker_usernames = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Shift
        fields = ['id', 'department', 'shift_type', 'start_time', 'end_time', 'workers', 'worker_usernames', 
                  'scheduled_by', 'auto_generated', 'status', 'notes', 'created_at', 'updated_at']

    def get_worker_usernames(self, obj):
        return [worker.user.username for worker in obj.workers.all()]

    def create(self, validated_data):
        workers = validated_data.pop('workers', [])
        shift = Shift.objects.create(**validated_data)
        shift.workers.set(workers)
        return shift

    def update(self, instance, validated_data):
        workers = validated_data.pop('workers', None)
        instance = super().update(instance, validated_data)
        if workers is not None:
            instance.workers.set(workers)
        return instance