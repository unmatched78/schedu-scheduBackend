# accounting/models.py
from django.db import models
from django_ledger.models import EntityModel

class AccountingEntity(EntityModel):
    organization = models.OneToOneField('scheduling.Organization', on_delete=models.CASCADE, related_name='accounting_entity')

    def __str__(self):
        return f"Accounting Entity for {self.organization.name}"

    class Meta:
        # Override to avoid inheriting EntityModel's indexes
        #indexes = []  # Or define your own, e.g., 
        [models.Index(fields=['organization'])]
        # Preserve other Meta options if needed
        verbose_name = "Accounting Entity"
        verbose_name_plural = "Accounting Entities"

class ReportSetting(models.Model):
    FREQUENCY_CHOICES = (
        ('daily', 'Daily'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    )

    entity = models.ForeignKey(AccountingEntity, on_delete=models.CASCADE, related_name='report_settings')
    name = models.CharField(max_length=100)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    start_day = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.frequency}) for {self.entity.organization.name}"