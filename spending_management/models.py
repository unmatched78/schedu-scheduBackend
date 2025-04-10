# spending_management/models.py
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class SpendingCategory(models.Model):
    CATEGORY_TYPES = (
        ('payroll', 'Payroll'),
        ('benefits', 'Benefits'),
        ('operational', 'Operational'),
        ('compliance', 'Compliance'),
        ('training', 'Training'),
        ('card', 'Corporate Card'),  # New type for card expenses
        ('other', 'Other'),
    )

    organization = models.ForeignKey('scheduling.Organization', on_delete=models.CASCADE, related_name='spending_categories')
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    description = models.TextField(blank=True)
    max_limit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # Optional max spending limit
    requires_approval = models.BooleanField(default=False)  # Whether expenses need approval
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.category_type}) - {self.organization.name}"

class Budget(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    organization = models.ForeignKey('scheduling.Organization', on_delete=models.CASCADE, related_name='budgets')
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_budgets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.organization.name} ({self.status})"

class BudgetAllocation(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='allocations')
    category = models.ForeignKey(SpendingCategory, on_delete=models.CASCADE)
    allocated_amount = models.DecimalField(max_digits=12, decimal_places=2)
    spent_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    warning_threshold = models.DecimalField(max_digits=5, decimal_places=2, default=80.0)  # % at which to warn (e.g., 80%)

    class Meta:
        unique_together = ('budget', 'category')

    def __str__(self):
        return f"{self.budget.name} - {self.category.name}: ${self.allocated_amount}"

class CorporateCard(models.Model):
    organization = models.ForeignKey('scheduling.Organization', on_delete=models.CASCADE, related_name='corporate_cards')
    card_number = models.CharField(max_length=16, unique=True)  # Simplified; in practice, encrypt this
    holder = models.ForeignKey('core.Worker', on_delete=models.CASCADE, related_name='cards')
    spending_limit = models.DecimalField(max_digits=12, decimal_places=2)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    issued_date = models.DateField()
    expiry_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Card {self.card_number[-4:]} - {self.holder.user.username}"

class Expense(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    organization = models.ForeignKey('scheduling.Organization', on_delete=models.CASCADE, related_name='expenses')
    category = models.ForeignKey(SpendingCategory, on_delete=models.CASCADE)
    budget = models.ForeignKey(Budget, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses')
    description = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    incurred_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_expenses')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_expenses')
    payroll_reference = models.ForeignKey('payroll_benefits.Payroll', on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses')
    card = models.ForeignKey(CorporateCard, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses')
    created_at = models.DateTimeField(auto_now_add=True)
    ledger_entry = models.ForeignKey('django_ledger.JournalEntryModel', on_delete=models.SET_NULL, null=True, blank=True, related_name='spending_expenses')
    
        
    def save(self, *args, **kwargs):
        if self.status == 'approved':
            if self.budget:
                allocation = BudgetAllocation.objects.get(budget=self.budget, category=self.category)
                allocation.spent_amount += self.amount
                if allocation.spent_amount > allocation.allocated_amount:
                    from ticketing.utils import send_automatic_notification
                    send_automatic_notification(
                        users=CustomUser.objects.filter(organization=self.organization, rolepermissions__permission='manage_organization'),
                        message=f"Alert: Spending in '{allocation.category.name}' (${allocation.spent_amount}) exceeds budget allocation (${allocation.allocated_amount})!"
                    )
                elif allocation.spent_amount >= (allocation.warning_threshold / 100) * allocation.allocated_amount:
                    from ticketing.utils import send_automatic_notification
                    send_automatic_notification(
                        users=CustomUser.objects.filter(organization=self.organization, rolepermissions__permission='manage_organization'),
                        message=f"Warning: Spending in '{allocation.category.name}' (${allocation.spent_amount}) nearing limit (${allocation.allocated_amount})."
                    )
                allocation.save()
            if self.card:
                self.card.current_balance += self.amount
                if self.card.current_balance > self.card.spending_limit:
                    from ticketing.utils import send_automatic_notification
                    send_automatic_notification(
                        users=[self.card.holder.user],
                        message=f"Alert: Corporate card balance (${self.card.current_balance}) exceeds limit (${self.card.spending_limit})!"
                    )
                self.card.save()
        super().save(*args, **kwargs)
 # Signals will handle ledger posting
    def __str__(self):
        return f"{self.description} - ${self.amount} ({self.category.name})"

# Signal to auto-import payroll expenses
@receiver(post_save, sender='payroll_benefits.Payroll')
def create_payroll_expense(sender, instance, created, **kwargs):
    if created:
        payroll_category, _ = SpendingCategory.objects.get_or_create(
            organization=instance.worker.organization,
            category_type='payroll',
            defaults={'name': 'Payroll Expenses'}
        )
        budget = Budget.objects.filter(
            organization=instance.worker.organization,
            start_date__lte=instance.created_at.date(),
            end_date__gte=instance.created_at.date(),
            status='approved'
        ).first()
        Expense.objects.create(
            organization=instance.worker.organization,
            category=payroll_category,
            budget=budget,
            description=f"Payroll for {instance.worker.user.username} - {instance.period}",
            amount=instance.total,
            incurred_date=instance.created_at.date(),
            status='approved',
            payroll_reference=instance
        )