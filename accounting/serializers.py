# # accounting/serializers.py
# from rest_framework import serializers
# from .models import AccountingEntity, ReportSetting

# class AccountingEntitySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = AccountingEntity
#         fields = ['id', 'organization', 'name', 'slug', 'created', 'updated']

# class ReportSettingSerializer(serializers.ModelSerializer):
#     entity_name = serializers.CharField(source='entity.organization.name', read_only=True)
#     class Meta:
#         model = ReportSetting
#         fields = ['id', 'entity', 'entity_name', 'name', 'frequency', 'start_day', 'created_at']
# accounting/serializers.py
from rest_framework import serializers
from .models import AccountingEntity, ReportSetting

class AccountingEntitySerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = AccountingEntity
        fields = ['id', 'organization', 'organization_name', 'name', 'slug', 'created', 'updated']

    def validate(self, data):
        if AccountingEntity.objects.filter(organization=data['organization']).exists():
            raise serializers.ValidationError("An accounting entity already exists for this organization.")
        return data

class ReportSettingSerializer(serializers.ModelSerializer):
    entity_name = serializers.CharField(source='entity.organization.name', read_only=True)

    class Meta:
        model = ReportSetting
        fields = ['id', 'entity', 'entity_name', 'name', 'frequency', 'start_day', 'created_at']

    def validate(self, data):
        if data['start_day'] < 1 or data['start_day'] > 31:
            raise serializers.ValidationError("Start day must be between 1 and 31.")
        return data