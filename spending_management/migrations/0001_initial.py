# Generated by Django 5.2 on 2025-04-04 23:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0002_initial'),
        ('payroll_benefits', '0001_initial'),
        ('scheduling', '0002_organization_created_at_organization_industry_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Budget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('pending_approval', 'Pending Approval'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='draft', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_budgets', to=settings.AUTH_USER_MODEL)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='budgets', to='scheduling.organization')),
            ],
        ),
        migrations.CreateModel(
            name='CorporateCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_number', models.CharField(max_length=16, unique=True)),
                ('spending_limit', models.DecimalField(decimal_places=2, max_digits=12)),
                ('current_balance', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('issued_date', models.DateField()),
                ('expiry_date', models.DateField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('holder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cards', to='core.worker')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='corporate_cards', to='scheduling.organization')),
            ],
        ),
        migrations.CreateModel(
            name='SpendingCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('category_type', models.CharField(choices=[('payroll', 'Payroll'), ('benefits', 'Benefits'), ('operational', 'Operational'), ('compliance', 'Compliance'), ('training', 'Training'), ('card', 'Corporate Card'), ('other', 'Other')], max_length=20)),
                ('description', models.TextField(blank=True)),
                ('max_limit', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('requires_approval', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='spending_categories', to='scheduling.organization')),
            ],
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('incurred_date', models.DateField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_expenses', to=settings.AUTH_USER_MODEL)),
                ('budget', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='expenses', to='spending_management.budget')),
                ('card', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='expenses', to='spending_management.corporatecard')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_expenses', to=settings.AUTH_USER_MODEL)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expenses', to='scheduling.organization')),
                ('payroll_reference', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='expenses', to='payroll_benefits.payroll')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spending_management.spendingcategory')),
            ],
        ),
        migrations.CreateModel(
            name='BudgetAllocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('allocated_amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('spent_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('warning_threshold', models.DecimalField(decimal_places=2, default=80.0, max_digits=5)),
                ('budget', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='allocations', to='spending_management.budget')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spending_management.spendingcategory')),
            ],
            options={
                'unique_together': {('budget', 'category')},
            },
        ),
    ]
