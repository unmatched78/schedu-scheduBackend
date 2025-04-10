from django.db import models
# Create your models here.
# compliance_legal/models.py
from django.conf import settings

class ComplianceRequirement(models.Model):
    REQUIREMENT_TYPES = (
        ('certification', 'Certification'),
        ('license', 'License'),
        ('regulation', 'Regulation'),
        ('training', 'Training'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('compliant', 'Compliant'),
        ('non_compliant', 'Non-Compliant'),
        ('expired', 'Expired'),
    )

    organization = models.ForeignKey('scheduling.Organization', on_delete=models.CASCADE, related_name='compliance_requirements')
    name = models.CharField(max_length=100)  # e.g., "HIPAA Certification", "OSHA Training"
    requirement_type = models.CharField(max_length=20, choices=REQUIREMENT_TYPES)
    description = models.TextField()
    due_date = models.DateField()  # When compliance is due
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_to = models.ForeignKey('core.Worker', on_delete=models.SET_NULL, null=True, blank=True, related_name='compliance_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.requirement_type}) - {self.organization.name}"

class LegalDocument(models.Model):
    DOCUMENT_TYPES = (
        ('contract', 'Contract'),
        ('policy', 'Policy'),
        ('agreement', 'Agreement'),
        ('certificate', 'Certificate'),
    )

    organization = models.ForeignKey('scheduling.Organization', on_delete=models.CASCADE, related_name='legal_documents')
    title = models.CharField(max_length=100)  # e.g., "Employee Contract 2025"
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='legal_documents/', null=True, blank=True)  # Store PDFs, etc.
    description = models.TextField(blank=True)
    effective_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_documents')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.document_type}) - {self.organization.name}"

class AuditLog(models.Model):
    ACTION_TYPES = (
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('review', 'Review'),
    )

    organization = models.ForeignKey('scheduling.Organization', on_delete=models.CASCADE, related_name='audit_logs')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    entity_type = models.CharField(max_length=50)  # e.g., "ComplianceRequirement", "LegalDocument"
    entity_id = models.IntegerField()  # ID of the affected entity
    details = models.TextField()  # e.g., "Updated status to compliant"
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='audit_actions')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action_type} on {self.entity_type} #{self.entity_id} by {self.performed_by.username if self.performed_by else 'N/A'}"