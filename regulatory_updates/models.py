# # regulatory_updates/models.py
# from django.db import models
# from django.conf import settings

# class RegulatoryUpdate(models.Model):
#     INDUSTRY_CHOICES = (
#         ('healthcare', 'Healthcare'),
#         ('finance', 'Finance'),
#         ('tech', 'Technology'),
#         ('manufacturing', 'Manufacturing'),
#         ('retail', 'Retail'),
#         ('other', 'Other'),
#     )
#     SOURCE_TYPES = (
#         ('regulation', 'Regulation'),
#         ('law', 'Law'),
#         ('trend', 'Industry Trend'),
#         ('news', 'News'),
#     )

#     title = models.CharField(max_length=200)
#     description = models.TextField()
#     source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
#     industry = models.CharField(max_length=20, choices=INDUSTRY_CHOICES)
#     source_url = models.URLField(blank=True, null=True)
#     published_date = models.DateField()
#     organizations = models.ManyToManyField('scheduling.Organization', related_name='regulatory_updates', blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.title} ({self.industry} - {self.source_type})"

# class UpdateAction(models.Model):
#     update = models.ForeignKey(RegulatoryUpdate, on_delete=models.CASCADE, related_name='actions')
#     organization = models.ForeignKey('scheduling.Organization', on_delete=models.CASCADE)
#     assigned_to = models.ForeignKey('core.Worker', on_delete=models.SET_NULL, null=True, blank=True)
#     ticket = models.ForeignKey('ticketing.Ticket', on_delete=models.SET_NULL, null=True, blank=True)  # Use existing Ticket
#     status = models.CharField(max_length=20, choices=(('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')), default='pending')
#     notes = models.TextField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Action for {self.update.title} - {self.organization.name}"
# regulatory_updates/models.py
from django.db import models
from django.conf import settings

class RegulatoryUpdate(models.Model):
    INDUSTRY_CHOICES = (
        ('healthcare', 'Healthcare'),
        ('finance', 'Finance'),
        ('tech', 'Technology'),
        ('manufacturing', 'Manufacturing'),
        ('retail', 'Retail'),
        ('other', 'Other'),
    )
    SOURCE_TYPES = (
        ('regulation', 'Regulation'),
        ('law', 'Law'),
        ('trend', 'Industry Trend'),
        ('news', 'News'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    industry = models.CharField(max_length=20, choices=INDUSTRY_CHOICES)
    source_url = models.URLField(blank=True, null=True)
    published_date = models.DateField()
    organizations = models.ManyToManyField('scheduling.Organization', related_name='regulatory_updates', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.industry} - {self.source_type})"

class UpdateAction(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )

    update = models.ForeignKey(RegulatoryUpdate, on_delete=models.CASCADE, related_name='actions')
    organization = models.ForeignKey('scheduling.Organization', on_delete=models.CASCADE)
    assigned_to = models.ForeignKey('core.Worker', on_delete=models.SET_NULL, null=True, blank=True)
    ticket = models.ForeignKey('ticketing.Ticket', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Action for {self.update.title} - {self.organization.name}"