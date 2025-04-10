# core/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class CustomRole(models.Model):
    name = models.CharField(max_length=100)
    organization = models.ForeignKey('scheduling.Organization', on_delete=models.CASCADE, related_name='custom_roles', null=True, blank=True)
    permissions = models.JSONField(default=list)  # e.g., ["manage_organization", "view_reports"]
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ('name', 'organization')

    def __str__(self):
        return f"{self.name} ({self.organization.name if self.organization else 'Global'})"

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=50, blank=True, null=True)
    organization = models.ForeignKey('scheduling.Organization', on_delete=models.SET_NULL, null=True, blank=True)
    selfreport_organisation = models.CharField(max_length=100, blank=True, null=True)
    custom_role = models.ForeignKey(CustomRole, on_delete=models.SET_NULL, null=True, blank=True, related_name='users_with_role')

    def get_roles(self):
        return [self.custom_role.name] if self.custom_role else []

    def has_permission(self, permission):
        return self.custom_role and permission in self.custom_role.permissions

    def has_role(self, role_name):
        return self.custom_role and self.custom_role.name == role_name
class Worker(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='worker_profile')
    department = models.ForeignKey('scheduling.Department', on_delete=models.SET_NULL, null=True, blank=True)
    position = models.CharField(max_length=100, blank=True, null=True)