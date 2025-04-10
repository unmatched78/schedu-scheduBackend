# payroll_benefits/models.py
from django.db import models
from django.conf import settings
import json

class Benefit(models.Model):
    BENEFIT_TYPES = (
        ('insurance', 'Insurance'),
        ('savings', 'Savings Account'),
        ('investment', 'Investment Plan'),
        ('other', 'Other'),
    )
    DEDUCTION_FREQUENCY = (
        ('monthly', 'Monthly'),
        ('biweekly', 'Biweekly'),
        ('yearly', 'Yearly'),
    )

    organization = models.ForeignKey('scheduling.Organization', on_delete=models.CASCADE, related_name='benefits')
    name = models.CharField(max_length=100)
    benefit_type = models.CharField(max_length=20, choices=BENEFIT_TYPES)
    description = models.TextField()
    default_cost = models.DecimalField(max_digits=10, decimal_places=2)
    deduction_frequency = models.CharField(max_length=20, choices=DEDUCTION_FREQUENCY, default='monthly')
    enrollment_start = models.DateField(null=True, blank=True)
    enrollment_end = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.benefit_type}) - {self.organization.name}"

class WorkerBenefit(models.Model):
    worker = models.ForeignKey('core.Worker', on_delete=models.CASCADE, related_name='enrolled_benefits')
    benefit = models.ForeignKey(Benefit, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    contribution_amount = models.DecimalField(max_digits=10, decimal_places=2)
    deduction_period = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('worker', 'benefit', 'deduction_period')

    def __str__(self):
        return f"{self.worker.user.username} enrolled in {self.benefit.name} for {self.deduction_period}"

class PayrollSettings(models.Model):
    worker = models.OneToOneField('core.Worker', on_delete=models.CASCADE, related_name='payroll_settings')
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    default_bonuses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    default_deductions = models.JSONField(default=dict)  # e.g., {"taxes": 500}
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payroll Settings for {self.worker.user.username}"

class Payroll(models.Model):
    worker = models.ForeignKey('core.Worker', on_delete=models.CASCADE, related_name='payrolls')
    period = models.CharField(max_length=50)
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    bonuses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    breakdown = models.JSONField(default=dict)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_total(self):
        deductions = sum(self.breakdown.values()) if self.breakdown else 0
        self.total = self.base_salary + self.bonuses - deductions

    def save(self, *args, **kwargs):
        if not self.pk:
            active_benefits = WorkerBenefit.objects.filter(
                worker=self.worker,
                is_active=True,
                deduction_period=self.period
            )
            benefit_deductions = {f"{benefit.benefit.name}": float(benefit.contribution_amount) for benefit in active_benefits}
            self.breakdown.update(benefit_deductions)
        self.calculate_total()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payroll for {self.worker.user.username} - {self.period}"