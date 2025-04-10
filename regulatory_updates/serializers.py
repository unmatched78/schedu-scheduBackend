# # regulatory_updates/serializers.py
# from rest_framework import serializers
# from .models import RegulatoryUpdate, UpdateAction

# class RegulatoryUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = RegulatoryUpdate
#         fields = ['id', 'title', 'description', 'source_type', 'industry', 'source_url', 'published_date', 'organizations', 'created_at']

# class UpdateActionSerializer(serializers.ModelSerializer):
#     update_title = serializers.CharField(source='update.title', read_only=True)
#     assigned_to_username = serializers.CharField(source='assigned_to.user.username', read_only=True)
#     ticket_title = serializers.CharField(source='ticket.title', read_only=True)
#     class Meta:
#         model = UpdateAction
#         fields = ['id', 'update', 'update_title', 'organization', 'assigned_to', 'assigned_to_username', 
#                   'ticket', 'ticket_title', 'status', 'notes', 'created_at', 'updated_at']
# regulatory_updates/serializers.py
from rest_framework import serializers
from .models import RegulatoryUpdate, UpdateAction

class RegulatoryUpdateSerializer(serializers.ModelSerializer):
    organization_names = serializers.SerializerMethodField()

    class Meta:
        model = RegulatoryUpdate
        fields = ['id', 'title', 'description', 'source_type', 'industry', 'source_url', 
                  'published_date', 'organizations', 'organization_names', 'created_at']

    def get_organization_names(self, obj):
        return [org.name for org in obj.organizations.all()]

class UpdateActionSerializer(serializers.ModelSerializer):
    update_title = serializers.CharField(source='update.title', read_only=True)
    assigned_to_username = serializers.CharField(source='assigned_to.user.username', read_only=True)
    ticket_title = serializers.CharField(source='ticket.title', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = UpdateAction
        fields = ['id', 'update', 'update_title', 'organization', 'organization_name', 
                  'assigned_to', 'assigned_to_username', 'ticket', 'ticket_title', 
                  'status', 'notes', 'created_at', 'updated_at']

    def validate(self, data):
        if data.get('assigned_to') and data['assigned_to'].organization != data['organization']:
            raise serializers.ValidationError("Assigned worker must belong to the same organization.")
        return data