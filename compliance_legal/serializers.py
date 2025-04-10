# # compliance_legal/serializers.py
# from rest_framework import serializers
# from .models import ComplianceRequirement, LegalDocument, AuditLog

# class ComplianceRequirementSerializer(serializers.ModelSerializer):
#     assigned_to_username = serializers.CharField(source='assigned_to.user.username', read_only=True)
#     class Meta:
#         model = ComplianceRequirement
#         fields = ['id', 'organization', 'name', 'requirement_type', 'description', 'due_date', 'status', 
#                   'assigned_to', 'assigned_to_username', 'created_at', 'updated_at']

# class LegalDocumentSerializer(serializers.ModelSerializer):
#     created_by_username = serializers.CharField(source='created_by.username', read_only=True)
#     class Meta:
#         model = LegalDocument
#         fields = ['id', 'organization', 'title', 'document_type', 'file', 'description', 'effective_date', 
#                   'expiry_date', 'created_by', 'created_by_username', 'created_at', 'updated_at']

# class AuditLogSerializer(serializers.ModelSerializer):
#     performed_by_username = serializers.CharField(source='performed_by.username', read_only=True)
#     class Meta:
#         model = AuditLog
#         fields = ['id', 'organization', 'action_type', 'entity_type', 'entity_id', 'details', 
#                   'performed_by', 'performed_by_username', 'timestamp']
# compliance_legal/serializers.py
from rest_framework import serializers
from .models import ComplianceRequirement, LegalDocument, AuditLog

class ComplianceRequirementSerializer(serializers.ModelSerializer):
    assigned_to_username = serializers.CharField(source='assigned_to.user.username', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = ComplianceRequirement
        fields = ['id', 'organization', 'organization_name', 'name', 'requirement_type', 'description', 
                  'due_date', 'status', 'assigned_to', 'assigned_to_username', 'created_at', 'updated_at']

    def validate(self, data):
        if data['due_date'] < timezone.now().date():
            raise serializers.ValidationError("Due date must be in the future at creation.")
        return data

class LegalDocumentSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = LegalDocument
        fields = ['id', 'organization', 'organization_name', 'title', 'document_type', 'file', 
                  'description', 'effective_date', 'expiry_date', 'created_by', 'created_by_username', 
                  'created_at', 'updated_at']

    def validate(self, data):
        if data['effective_date'] > data.get('expiry_date', timezone.now().date() + timezone.timedelta(days=365)):
            raise serializers.ValidationError("Expiry date must be after effective date.")
        return data

class AuditLogSerializer(serializers.ModelSerializer):
    performed_by_username = serializers.CharField(source='performed_by.username', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = AuditLog
        fields = ['id', 'organization', 'organization_name', 'action_type', 'entity_type', 'entity_id', 
                  'details', 'performed_by', 'performed_by_username', 'timestamp']