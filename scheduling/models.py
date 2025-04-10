# scheduling/models.py
from django.db import models
from django.conf import settings

class Organization(models.Model):
    INDUSTRY_CHOICES = (
        ('healthcare', 'Healthcare'),
        ('finance', 'Finance'),
        ('tech', 'Technology'),
        ('manufacturing', 'Manufacturing'),
        ('retail', 'Retail'),
        ('education', 'Education'),
        ('hospitality', 'Hospitality'),
        ('other', 'Other'),
    )

    name = models.CharField(max_length=255)
    industry = models.CharField(max_length=20, choices=INDUSTRY_CHOICES, default='healthcare')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.industry})"

class DepartmentShiftSettings(models.Model):
    SHIFT_SWAP_CHOICES = (
        ('automatic', 'Automatic'),
        ('review', 'Review'),
    )
    
    department = models.OneToOneField('Department', on_delete=models.CASCADE, related_name='shift_settings')
    shift_swap_policy = models.CharField(max_length=10, choices=SHIFT_SWAP_CHOICES, default='review')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.department.name} - {self.shift_swap_policy}"

class Department(models.Model):
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE, related_name='departments', null=True, blank=True)
    name = models.CharField(max_length=100)
    head = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_department')
    is_independent = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not hasattr(self, 'shift_settings'):
            DepartmentShiftSettings.objects.create(department=self)

    def __str__(self):
        return f"{self.name} ({self.organization.name if self.organization else 'Independent'})"

class Shift(models.Model):
    SHIFT_TYPES = (
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('night', 'Night'),
    )
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='shifts')
    shift_type = models.CharField(max_length=50, choices=SHIFT_TYPES)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    workers = models.ManyToManyField('core.Worker', related_name='shifts')
    scheduled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    auto_generated = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.shift_type} Shift - {self.start_time}"

class ShiftSwapRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
    )
    
    original_shift = models.ForeignKey('Shift', on_delete=models.CASCADE, related_name='swap_requests_from')
    requested_shift = models.ForeignKey('Shift', on_delete=models.CASCADE, related_name='swap_requests_to')
    requester = models.ForeignKey('core.Worker', on_delete=models.CASCADE, related_name='shift_swap_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='shift_swap_reviews')

    def __str__(self):
        return f"Swap Request: {self.original_shift} to {self.requested_shift}"