from django.db import models
from django.conf import settings
from rolepermissions.checkers import has_permission
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField
# from django.contrib.auth import get_user_model
User = settings.AUTH_USER_MODEL
# Base model for automatic timestamping.
class Timer(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


# Organization registration (e.g., a hospital, clinic, or other entity)
class Organization(models.Model):
    name = models.CharField(max_length=255)
    # Additional fields such as address, contact info, etc.
    
    def __str__(self):
        return self.name
# Custom user model (teacher and potential other roles).
class CustomUser(AbstractUser):
    phone = models.CharField(max_length=50)
    organization=models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)#if the organisation is not registered as full but for example a departmenet chief wants to use our system for thier departmenet persoanlly
    selfreport_organisation=models.CharField(max_length=100)#here in a case no registered we will prompt to name where they work exiplicitly.
    #role:, I think as you have told me, it will be handled smoooth, right ?
    def __str__(self):
        return self.username
# Department model: each department is part of an organization.
class Department(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='departments',null=True, blank=True
    )
    name = models.CharField(max_length=100)
    # Department head – typically a user assigned the DepartmentHead role.
    head = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_department'
    )

    def __str__(self):
        return f"{self.name} ({self.organization.name})"

# Worker model: connects a user to a department.
class Worker(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='worker_profile'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='workers'
    )
    position = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

# Shift model with ManyToMany relation for workers and integrated role permission checks.
class Shift(models.Model):
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='shifts'
    )
    shift_type = models.CharField(
        max_length=50,
        choices=(
            ('morning', 'Morning Shift'),
            ('afternoon', 'Afternoon Shift'),
            ('night', 'Night Shift'),
            ('day', 'Day Shift')
        ),
        default='morning'
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    # A shift can have one or more workers assigned.
    workers = models.ManyToManyField(
        Worker,
        related_name='shifts'
    )
    scheduled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='scheduled_shifts'
    )
    auto_generated = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=(
            ('scheduled', 'Scheduled'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled')
        ),
        default='scheduled'
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Ensure that the user scheduling the shift has sufficient permissions.
        if self.scheduled_by:
            # Check if the user is a DepartmentHead, OrganizationAdmin, or MainAdmin.
            if not (
                has_permission(self.scheduled_by, 'manage_department') or 
                has_permission(self.scheduled_by, 'manage_organization') or 
                has_permission(self.scheduled_by, 'manage_all')
            ):
                raise PermissionError("User does not have permission to schedule shifts.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.shift_type.capitalize()} shift on {self.start_time.strftime('%Y-%m-%d')} for {self.department.name}"
    
    class Meta:
        ordering = ['start_time']


















# class GetStarted(Timer):#will also be used for request a demo and waitlist joining
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     email = models.EmailField(max_length=254)
#     phone_number=models.CharField(max_length=50)
#     message=models.TextField(null=True, blank=True)
#     school=models.TextField(null=True, blank=True)
#     def __str__(self):
#         return f"Get started request by {self.first_name} {self.last_name}"
#     class Meta:
#         ordering = ['-created_at']
    