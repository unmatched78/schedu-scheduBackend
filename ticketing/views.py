# # ticketing/views.py
# from rest_framework import generics, status
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from django.shortcuts import get_object_or_404
# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync
# from .models import Ticket, TicketResponse, Notification
# from .serializers import TicketSerializer, TicketResponseSerializer, NotificationSerializer
# from .utils import send_automatic_notification
# from rolepermissions.checkers import has_permission
# from core.models import CustomUser

# class TicketCreateAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         serializer = TicketSerializer(data=request.data)
#         if serializer.is_valid():
#             ticket_type = serializer.validated_data['ticket_type']
            
#             if ticket_type == 'global' and not has_permission(request.user, 'manage_all'):
#                 return Response({"error": "Permission denied."}, status=403)
#             elif ticket_type == 'organization' and not has_permission(request.user, 'manage_organization'):
#                 return Response({"error": "Permission denied."}, status=403)
#             elif ticket_type == 'department' and not has_permission(request.user, 'manage_department'):
#                 return Response({"error": "Permission denied."}, status=403)

#             ticket = serializer.save(worker=request.user.worker_profile if hasattr(request.user, 'worker_profile') else None)
            
#             # Manual notifications via WebSocket
#             channel_layer = get_channel_layer()
#             message = f"New {ticket_type} ticket: {ticket.title}"
#             notification_data = {
#                 'type': 'send_notification',
#                 'notification_id': None,
#                 'message': message,
#                 'ticket_id': ticket.id,
#                 'created_at': ticket.created_at.isoformat(),
#                 'is_read': False,
#                 'is_automatic': False
#             }

#             if ticket_type == 'global':
#                 group = 'global'
#                 users = CustomUser.objects.all()
#             elif ticket_type == 'organization':
#                 group = f"org_{ticket.organization.id}"
#                 users = CustomUser.objects.filter(organization=ticket.organization)
#             elif ticket_type == 'department':
#                 group = f"dept_{ticket.department.id}"
#                 users = CustomUser.objects.filter(worker_profile__department=ticket.department)
#             elif ticket_type == 'user':
#                 group = f"user_{ticket.target_user.id}" if ticket.target_user else None
#                 users = [ticket.target_user] if ticket.target_user else []
#             else:  # question
#                 group = f"user_{ticket.worker.user.id}" if ticket.worker else None
#                 users = [ticket.worker.user] if ticket.worker else []

#             for user in users:
#                 notification = Notification.objects.create(user=user, ticket=ticket, message=message)
#                 notification_data['notification_id'] = notification.id
#                 notification_data['created_at'] = notification.created_at.isoformat()
#                 target_group = f"user_{user.id}" if ticket_type in ['user', 'question'] else group
#                 async_to_sync(channel_layer.group_send)(
#                     target_group,
#                     notification_data
#                 )
            
#             return Response(serializer.data, status=201)
#         return Response(serializer.errors, status=400)

# class TicketResponseCreateAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, ticket_id):
#         ticket = get_object_or_404(Ticket, id=ticket_id)
#         serializer = TicketResponseSerializer(data=request.data)
#         if serializer.is_valid():
#             response = serializer.save(ticket=ticket, responder=request.user)
            
#             # Notify relevant users
#             message = f"New response to ticket '{ticket.title}' by {request.user.username}"
#             notify_users = {ticket.worker.user} if ticket.worker else set()
#             if ticket.target_user:
#                 notify_users.add(ticket.target_user)
#             if ticket.ticket_type == 'question':
#                 notify_users.add(ticket.worker.user)
            
#             send_automatic_notification(
#                 users=[user for user in notify_users if user != request.user],
#                 message=message,
#                 ticket=ticket
#             )
            
#             return Response(serializer.data, status=201)
#         return Response(serializer.errors, status=400)

# class TicketListAPIView(generics.ListAPIView):
#     serializer_class = TicketSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         if has_permission(user, 'manage_all'):
#             return Ticket.objects.all()
#         elif has_permission(user, 'manage_organization'):
#             return Ticket.objects.filter(organization=user.organization)
#         elif has_permission(user, 'manage_department'):
#             return Ticket.objects.filter(department=user.managed_department)
#         return Ticket.objects.filter(worker__user=user) | Ticket.objects.filter(target_user=user)

# class NotificationListAPIView(generics.ListAPIView):
#     serializer_class = NotificationSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return Notification.objects.filter(user=self.request.user)
# ticketing/views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Ticket, TicketResponse, Notification
from .serializers import TicketSerializer, TicketResponseSerializer, NotificationSerializer
from .utils import send_automatic_notification
from core.permissions import require_permission, has_permission
from core.models import CustomUser

class TicketCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @require_permission('create_tickets')
    def post(self, request):
        serializer = TicketSerializer(data=request.data)
        if serializer.is_valid():
            ticket_type = serializer.validated_data['ticket_type']
            
            if ticket_type == 'global' and not has_permission(request.user, 'manage_all'):
                return Response({"error": "Permission denied for global tickets."}, status=403)
            elif ticket_type == 'organization' and not has_permission(request.user, 'manage_organization'):
                return Response({"error": "Permission denied for organization tickets."}, status=403)
            elif ticket_type == 'department' and not has_permission(request.user, 'manage_department'):
                return Response({"error": "Permission denied for department tickets."}, status=403)

            ticket = serializer.save(worker=request.user.worker_profile if hasattr(request.user, 'worker_profile') else None)
            
            # Manual notifications via WebSocket
            channel_layer = get_channel_layer()
            message = f"New {ticket_type} ticket: {ticket.title}"
            notification_data = {
                'type': 'send_notification',
                'notification_id': None,
                'message': message,
                'ticket_id': ticket.id,
                'created_at': ticket.created_at.isoformat(),
                'is_read': False,
                'is_automatic': False
            }

            if ticket_type == 'global':
                group = 'global'
                users = CustomUser.objects.all()
            elif ticket_type == 'organization':
                group = f"org_{ticket.organization.id}"
                users = CustomUser.objects.filter(organization=ticket.organization)
            elif ticket_type == 'department':
                group = f"dept_{ticket.department.id}"
                users = CustomUser.objects.filter(worker_profile__department=ticket.department)
            elif ticket_type == 'user':
                group = f"user_{ticket.target_user.id}" if ticket.target_user else None
                users = [ticket.target_user] if ticket.target_user else []
            else:  # question or regulatory
                group = f"user_{ticket.worker.user.id}" if ticket.worker else None
                users = [ticket.worker.user] if ticket.worker else []

            for user in users:
                notification = Notification.objects.create(user=user, ticket=ticket, message=message)
                notification_data['notification_id'] = notification.id
                notification_data['created_at'] = notification.created_at.isoformat()
                target_group = f"user_{user.id}" if ticket_type in ['user', 'question', 'regulatory'] else group
                async_to_sync(channel_layer.group_send)(
                    target_group,
                    notification_data
                )
            
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class TicketResponseCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @require_permission('respond_to_tickets')
    def post(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, id=ticket_id)
        serializer = TicketResponseSerializer(data=request.data)
        if serializer.is_valid():
            response = serializer.save(ticket=ticket, responder=request.user)
            
            # Notify relevant users
            message = f"New response to ticket '{ticket.title}' by {request.user.username}"
            notify_users = {ticket.worker.user} if ticket.worker else set()
            if ticket.target_user:
                notify_users.add(ticket.target_user)
            if ticket.ticket_type == 'question':
                notify_users.add(ticket.worker.user)
            
            send_automatic_notification(
                users=[user for user in notify_users if user != request.user],
                message=message,
                ticket=ticket
            )
            
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class TicketListAPIView(generics.ListAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if has_permission(user, 'view_all_tickets'):
            if has_permission(user, 'manage_all'):
                return Ticket.objects.all()
            elif has_permission(user, 'manage_organization'):
                return Ticket.objects.filter(organization=user.organization)
            elif has_permission(user, 'manage_department'):
                return Ticket.objects.filter(department=user.managed_department)
        return Ticket.objects.filter(worker__user=user) | Ticket.objects.filter(target_user=user)

class NotificationListAPIView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if has_permission(self.request.user, 'view_notifications'):
            return Notification.objects.filter(user=self.request.user)
        return Notification.objects.none()