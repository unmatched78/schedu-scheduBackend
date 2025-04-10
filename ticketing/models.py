# # ticketing/models.py
# from django.db import models
# from django.conf import settings
# from scheduling.models import Organization, Department

# class Ticket(models.Model):
#     TICKET_TYPES = (
#         ('global', 'Global'),
#         ('organization', 'Organization'),
#         ('department', 'Department'),
#         ('user', 'User'),
#         ('question', 'Question'),
#         ('regulatory', 'Regulatory'),  # New type for regulatory updates
#     )
#     STATUS_CHOICES = (
#         ('open', 'Open'),
#         ('in_progress', 'In Progress'),
#         ('resolved', 'Resolved'),
#         ('closed', 'Closed'),
#     )
    
#     worker = models.ForeignKey('core.Worker', on_delete=models.CASCADE, related_name='tickets', null=True, blank=True)
#     title = models.CharField(max_length=200)
#     description = models.TextField()
#     ticket_type = models.CharField(max_length=20, choices=TICKET_TYPES, default='user')
#     organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
#     department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
#     target_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='targeted_tickets')
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
#     assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
#     regulatory_update = models.ForeignKey('regulatory_updates.RegulatoryUpdate', on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')  # Link to regulatory updates
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.title} ({self.ticket_type})"

# class TicketResponse(models.Model):
#     ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='responses')
#     responder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     content = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)

# class Notification(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
#     ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=True, blank=True)
#     message = models.TextField()
#     is_read = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     is_automatic = models.BooleanField(default=False)

#     def __str__(self):
#         return f"Notification for {self.user.username}: {self.message}"
# ticketing/models.py
from django.db import models
from django.conf import settings
from scheduling.models import Organization, Department

class Ticket(models.Model):
    TICKET_TYPES = (
        ('global', 'Global'),
        ('organization', 'Organization'),
        ('department', 'Department'),
        ('user', 'User'),
        ('question', 'Question'),
        ('regulatory', 'Regulatory'),
    )
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    
    worker = models.ForeignKey('core.Worker', on_delete=models.CASCADE, related_name='tickets', null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    ticket_type = models.CharField(max_length=20, choices=TICKET_TYPES, default='user')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    target_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='targeted_tickets')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    regulatory_update = models.ForeignKey('regulatory_updates.RegulatoryUpdate', on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.ticket_type})"

class TicketResponse(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='responses')
    responder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response to {self.ticket.title} by {self.responder.username}"

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_automatic = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:50]}..."