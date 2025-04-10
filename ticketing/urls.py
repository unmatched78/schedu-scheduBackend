# ticketing/urls.py
from django.urls import path
from .views import TicketCreateAPIView, TicketListAPIView, TicketResponseCreateAPIView, NotificationListAPIView

urlpatterns = [
    path('tickets/create/', TicketCreateAPIView.as_view(), name='create-ticket'),
    path('tickets/', TicketListAPIView.as_view(), name='list-tickets'),
    path('tickets/<int:ticket_id>/respond/', TicketResponseCreateAPIView.as_view(), name='respond-ticket'),
    path('notifications/', NotificationListAPIView.as_view(), name='list-notifications'),
]