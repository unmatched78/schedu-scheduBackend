# # regulatory_updates/views.py
# from rest_framework import generics, status
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from django.core.exceptions import PermissionDenied
# from .models import RegulatoryUpdate, UpdateAction
# from .serializers import RegulatoryUpdateSerializer, UpdateActionSerializer
# from ticketing.models import Ticket
# from rolepermissions.checkers import has_permission
# from core.models import Worker, CustomUser
# from scheduling.models import Organization
# from ticketing.utils import send_automatic_notification
# import requests

# class RegulatoryUpdateListAPIView(generics.ListAPIView):
#     serializer_class = RegulatoryUpdateSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         if has_permission(user, 'manage_organization'):
#             return RegulatoryUpdate.objects.filter(organizations=user.organization)
#         return RegulatoryUpdate.objects.filter(organizations=user.organization, actions__assigned_to=user.worker_profile)

# class RegulatoryUpdateCreateAPIView(generics.CreateAPIView):
#     serializer_class = RegulatoryUpdateSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         if not has_permission(self.request.user, 'manage_organization'):
#             raise PermissionDenied("Permission denied.")
#         update = serializer.save()
#         update.organizations.add(self.request.user.organization)
#         send_automatic_notification(
#             users=CustomUser.objects.filter(organization=self.request.user.organization, rolepermissions__permission='manage_organization'),
#             message=f"New regulatory update: '{update.title}' ({update.industry}) added by {self.request.user.username}."
#         )

# class UpdateActionCreateAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         update_id = request.data.get('update_id')
#         assigned_to_id = request.data.get('assigned_to')
#         notes = request.data.get('notes', '')

#         update = RegulatoryUpdate.objects.get(id=update_id, organizations=request.user.organization)
#         if not has_permission(self.request.user, 'manage_organization'):
#             raise PermissionDenied("Permission denied.")

#         assigned_to = Worker.objects.get(id=assigned_to_id) if assigned_to_id else None
#         ticket = Ticket.objects.create(
#             title=f"Action Required: {update.title}",
#             description=f"Regulatory update: {update.description}\nNotes: {notes}",
#             ticket_type='regulatory',
#             organization=request.user.organization,
#             assigned_to=assigned_to.user if assigned_to else None,
#             status='open',
#             regulatory_update=update
#         )
#         action = UpdateAction.objects.create(
#             update=update,
#             organization=request.user.organization,
#             assigned_to=assigned_to,
#             ticket=ticket,
#             notes=notes
#         )
#         if assigned_to:
#             send_automatic_notification(
#                 users=[assigned_to.user],
#                 message=f"You’ve been assigned a task for '{update.title}': {notes or 'Review and take action.'}"
#             )
#         return Response(UpdateActionSerializer(action).data, status=201)

# class UpdateActionListAPIView(generics.ListAPIView):
#     serializer_class = UpdateActionSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         if has_permission(user, 'manage_organization'):
#             return UpdateAction.objects.filter(organization=user.organization)
#         return UpdateAction.objects.filter(assigned_to=user.worker_profile)

# class FetchRegulatoryUpdatesAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         if not has_permission(request.user, 'manage_organization'):
#             raise PermissionDenied("Permission denied.")
        
#         # Placeholder: Replace with real API
#         response = requests.get("https://api.regulatorysource.com/updates")
#         if response.status_code == 200:
#             updates = response.json()
#             org = request.user.organization
#             for update_data in updates:
#                 if update_data.get('industry') == org.industry:  # Match organization’s industry
#                     update, created = RegulatoryUpdate.objects.get_or_create(
#                         title=update_data['title'],
#                         source_type=update_data.get('type', 'regulation'),
#                         industry=update_data['industry'],
#                         defaults={
#                             'description': update_data['description'],
#                             'source_url': update_data.get('url'),
#                             'published_date': update_data['date']
#                         }
#                     )
#                     if created:
#                         update.organizations.add(org)
#                         send_automatic_notification(
#                             users=CustomUser.objects.filter(organization=org, rolepermissions__permission='manage_organization'),
#                             message=f"New regulatory update fetched: '{update.title}' ({update.industry}) tailored for {org.industry}."
#                         )
#         return Response({"status": f"Updates fetched for {org.industry} industry."}, status=200)
# regulatory_updates/views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import PermissionDenied
from .models import RegulatoryUpdate, UpdateAction
from .serializers import RegulatoryUpdateSerializer, UpdateActionSerializer
from ticketing.models import Ticket
from core.permissions import require_permission, has_permission
from core.models import Worker, CustomUser
from scheduling.models import Organization
from ticketing.utils import send_automatic_notification
import requests

class RegulatoryUpdateListAPIView(generics.ListAPIView):
    serializer_class = RegulatoryUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if has_permission(user, 'view_regulatory_updates'):
            if has_permission(user, 'manage_organization'):
                return RegulatoryUpdate.objects.filter(organizations=user.organization)
            return RegulatoryUpdate.objects.filter(organizations=user.organization, actions__assigned_to=user.worker_profile)
        return RegulatoryUpdate.objects.none()

class RegulatoryUpdateCreateAPIView(generics.CreateAPIView):
    serializer_class = RegulatoryUpdateSerializer
    permission_classes = [IsAuthenticated]

    @require_permission('create_regulatory_updates')
    def perform_create(self, serializer):
        update = serializer.save()
        update.organizations.add(self.request.user.organization)
        org_admins = CustomUser.objects.filter(
            organization=self.request.user.organization,
            custom_role__permissions__contains=['manage_organization']
        )
        send_automatic_notification(
            users=org_admins,
            message=f"New regulatory update: '{update.title}' ({update.industry}) added by {self.request.user.username}."
        )

class UpdateActionCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @require_permission('create_update_actions')
    def post(self, request):
        update_id = request.data.get('update_id')
        assigned_to_id = request.data.get('assigned_to')
        notes = request.data.get('notes', '')

        try:
            update = RegulatoryUpdate.objects.get(id=update_id, organizations=request.user.organization)
        except RegulatoryUpdate.DoesNotExist:
            return Response({"error": "Regulatory update not found or not in your organization."}, status=404)

        assigned_to = Worker.objects.get(id=assigned_to_id) if assigned_to_id else None
        ticket = Ticket.objects.create(
            title=f"Action Required: {update.title}",
            description=f"Regulatory update: {update.description}\nNotes: {notes}",
            ticket_type='regulatory',
            organization=request.user.organization,
            assigned_to=assigned_to.user if assigned_to else None,
            status='open',
            regulatory_update=update
        )
        action = UpdateAction.objects.create(
            update=update,
            organization=request.user.organization,
            assigned_to=assigned_to,
            ticket=ticket,
            notes=notes
        )
        if assigned_to:
            send_automatic_notification(
                users=[assigned_to.user],
                message=f"You’ve been assigned a task for '{update.title}': {notes or 'Review and take action.'}"
            )
        return Response(UpdateActionSerializer(action).data, status=201)

class UpdateActionListAPIView(generics.ListAPIView):
    serializer_class = UpdateActionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if has_permission(user, 'view_update_actions'):
            if has_permission(user, 'manage_organization'):
                return UpdateAction.objects.filter(organization=user.organization)
            return UpdateAction.objects.filter(assigned_to=user.worker_profile)
        return UpdateAction.objects.none()

class FetchRegulatoryUpdatesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @require_permission('fetch_regulatory_updates')
    def get(self, request):
        org = request.user.organization
        if not org:
            return Response({"error": "User not associated with an organization."}, status=400)

        # Placeholder: Replace with real API
        try:
            response = requests.get("https://api.regulatorysource.com/updates")
            if response.status_code == 200:
                updates = response.json()
                for update_data in updates:
                    if update_data.get('industry') == org.industry:
                        update, created = RegulatoryUpdate.objects.get_or_create(
                            title=update_data['title'],
                            source_type=update_data.get('type', 'regulation'),
                            industry=update_data['industry'],
                            defaults={
                                'description': update_data['description'],
                                'source_url': update_data.get('url'),
                                'published_date': update_data['date']
                            }
                        )
                        if created:
                            update.organizations.add(org)
                            org_admins = CustomUser.objects.filter(
                                organization=org,
                                custom_role__permissions__contains=['manage_organization']
                            )
                            send_automatic_notification(
                                users=org_admins,
                                message=f"New regulatory update fetched: '{update.title}' ({update.industry}) tailored for {org.industry}."
                            )
                return Response({"status": f"Updates fetched for {org.industry} industry."}, status=200)
            else:
                return Response({"error": "Failed to fetch updates from source."}, status=response.status_code)
        except requests.RequestException as e:
            return Response({"error": f"Error fetching updates: {str(e)}"}, status=500)