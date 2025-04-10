# accounting/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import AccountingEntity, ReportSetting
from ticketing.utils import send_automatic_notification
from core.models import CustomUser

@shared_task
def generate_automated_reports():
    today = timezone.now().date()
    for setting in ReportSetting.objects.all():
        entity = setting.entity
        should_run = False
        
        if setting.frequency == 'daily':
            should_run = True
        elif setting.frequency == 'monthly' and today.day == setting.start_day:
            should_run = True
        elif setting.frequency == 'quarterly' and today.day == setting.start_day and today.month in [1, 4, 7, 10]:
            should_run = True
        elif setting.frequency == 'yearly' and today.day == setting.start_day and today.month == 1:
            should_run = True

        if should_run:
            to_date = today
            if setting.frequency == 'daily':
                from_date = to_date - timedelta(days=1)
            elif setting.frequency == 'monthly':
                from_date = to_date.replace(day=1)
            elif setting.frequency == 'quarterly':
                from_date = to_date - timedelta(days=90)
            elif setting.frequency == 'yearly':
                from_date = to_date.replace(month=1, day=1)

            balance_sheet = entity.get_balance_sheet(to_date=to_date)
            income_statement = entity.get_income_statement(from_date=from_date, to_date=to_date)
            
            report_summary = (
                f"Automated {setting.frequency} Report ({setting.name}):\n"
                f"From {from_date} to {to_date}\n"
                f"Assets: ${balance_sheet['assets']}\n"
                f"Liabilities: ${balance_sheet['liabilities']}\n"
                f"Net Income: ${income_statement['net_income']}"
            )
            
            send_automatic_notification(
                users=CustomUser.objects.filter(organization=entity.organization, rolepermissions__permission='manage_organization'),
                message=report_summary
            )