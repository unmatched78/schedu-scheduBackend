# # ticketing/serializers.py
# from rest_framework import serializers
# from .models import Ticket, TicketResponse, Notification

# class TicketResponseSerializer(serializers.ModelSerializer):
#     responder_username = serializers.CharField(source='responder.username', read_only=True)
#     class Meta:
#         model = TicketResponse
#         fields = ['id', 'ticket', 'responder','responder_username', 'content', 'created_at']
#         read_only_fields = ['responder', 'created_at']

# class TicketSerializer(serializers.ModelSerializer):
#     responses = TicketResponseSerializer(many=True, read_only=True)
#     assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True)
#     regulatory_update_title = serializers.CharField(source='regulatory_update.title', read_only=True)
#     class Meta:
#         model = Ticket
#         fields = ['id', 'worker', 'title', 'description', 'ticket_type', 'organization', 'department', 
#                   'assigned_to_username', 'regulatory_update', 'regulatory_update_title',
#                   'target_user', 'status', 'assigned_to', 'created_at', 'updated_at', 'responses']
#         read_only_fields = ['worker', 'created_at', 'updated_at']

# class NotificationSerializer(serializers.ModelSerializer):
#     ticket_title = serializers.CharField(source='ticket.title', read_only=True)
#     class Meta:
#         model = Notification
        
#         fields = ['id', 'user', 'ticket', 'message', 'is_read','ticket_title', 'created_at', 'is_automatic']
#         read_only_fields = ['user', 'created_at', 'is_automatic']
        
# ticketing/serializers.py
from rest_framework import serializers
from .models import Ticket, TicketResponse, Notification

class TicketResponseSerializer(serializers.ModelSerializer):
    responder_username = serializers.CharField(source='responder.username', read_only=True)

    class Meta:
        model = TicketResponse
        fields = ['id', 'ticket', 'responder', 'responder_username', 'content', 'created_at']
        read_only_fields = ['responder', 'created_at']

class TicketSerializer(serializers.ModelSerializer):
    responses = TicketResponseSerializer(many=True, read_only=True)
    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True)
    regulatory_update_title = serializers.CharField(source='regulatory_update.title', read_only=True)
    worker_username = serializers.CharField(source='worker.user.username', read_only=True)
    target_user_username = serializers.CharField(source='target_user.username', read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'worker', 'worker_username', 'title', 'description', 'ticket_type', 'organization', 
                  'department', 'assigned_to_username', 'regulatory_update', 'regulatory_update_title',
                  'target_user', 'target_user_username', 'status', 'assigned_to', 'created_at', 
                  'updated_at', 'responses']
        read_only_fields = ['worker', 'created_at', 'updated_at']

    def validate(self, data):
        ticket_type = data.get('ticket_type')
        if ticket_type == 'organization' and not data.get('organization'):
            raise serializers.ValidationError("Organization is required for organization tickets.")
        if ticket_type == 'department' and not data.get('department'):
            raise serializers.ValidationError("Department is required for department tickets.")
        if ticket_type == 'user' and not data.get('target_user'):
            raise serializers.ValidationError("Target user is required for user tickets.")
        return data

class NotificationSerializer(serializers.ModelSerializer):
    ticket_title = serializers.CharField(source='ticket.title', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'user', 'ticket', 'ticket_title', 'message', 'is_read', 'created_at', 'is_automatic']
        read_only_fields = ['user', 'created_at', 'is_automatic']