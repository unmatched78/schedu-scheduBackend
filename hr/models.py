# hr/models.py
# hr/models.py
from django.db import models
from django.conf import settings

class Payslip(models.Model):
    worker = models.ForeignKey('core.Worker', on_delete=models.CASCADE, related_name='payslips')
    period = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payslip for {self.worker.user.username} - {self.period}"

class LeaveRequest(models.Model):
    worker = models.ForeignKey('core.Worker', on_delete=models.CASCADE, related_name='leave_requests')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=(('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')), default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Leave Request by {self.worker.user.username} ({self.start_date} to {self.end_date})"

class CompanyPolicy(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    organization = models.ForeignKey('scheduling.Organization', on_delete=models.CASCADE, related_name='policies', null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.organization.name if self.organization else 'No Org'}"

class PerformanceReview(models.Model):
    worker = models.ForeignKey('core.Worker', on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='given_reviews')
    score = models.IntegerField()
    comments = models.TextField()
    review_date = models.DateField()

    def __str__(self):
        return f"Review for {self.worker.user.username} by {self.reviewer.username if self.reviewer else 'N/A'}"

class Goal(models.Model):
    worker = models.ForeignKey('core.Worker', on_delete=models.CASCADE, related_name='goals')
    description = models.TextField()
    deadline = models.DateField()
    status = models.CharField(max_length=20, choices=(('pending', 'Pending'), ('completed', 'Completed')), default='pending')

    def __str__(self):
        return f"Goal for {self.worker.user.username}: {self.description[:20]}..."