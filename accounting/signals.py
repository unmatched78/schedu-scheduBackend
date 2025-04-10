# # accounting/signals.py
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django_ledger.models import LedgerModel, JournalEntryModel, TransactionModel
# from spending_management.models import Expense, CorporateCard
# from payroll_benefits.models import Payroll
# from .models import AccountingEntity
# from django.core.exceptions import ObjectDoesNotExist

# @receiver(post_save, sender=Expense)
# def sync_expense_to_ledger(sender, instance, created, **kwargs):
#     if instance.status == 'approved' and not hasattr(instance, 'ledger_entry'):
#         try:
#             entity = AccountingEntity.objects.get(organization=instance.organization)
#             ledger = LedgerModel.objects.get_or_create(entity=entity, name=f"{entity.organization.name} General Ledger")[0]
            
#             journal_entry = JournalEntryModel.objects.create(
#                 ledger=ledger,
#                 description=instance.description,
#                 timestamp=instance.created_at,
#                 entity=entity
#             )
            
#             # Simplified accounts (configure these in Django Ledger)
#             expense_account = entity.get_coa_account(code='6000')  # Example: Expense account
#             cash_account = entity.get_coa_account(code='1000')     # Example: Cash account
#             liability_account = entity.get_coa_account(code='2000') # Example: Card liability
            
#             transactions = [
#                 {'account': expense_account, 'amount': instance.amount, 'tx_type': TransactionModel.TX_TYPE_DEBIT},
#                 {'account': cash_account if not instance.card else liability_account, 
#                  'amount': instance.amount, 'tx_type': TransactionModel.TX_TYPE_CREDIT}
#             ]
#             journal_entry.post(transactions=transactions)
            
#             instance.ledger_entry = journal_entry
#             instance.save()
            
#             from ticketing.utils import send_automatic_notification
#             send_automatic_notification(
#                 users=entity.organization.users.filter(rolepermissions__permission='manage_organization'),
#                 message=f"Expense '{instance.description}' (${instance.amount}) posted to ledger."
#             )
#         except ObjectDoesNotExist:
#             pass  # Handle missing entity/ledger gracefully

# @receiver(post_save, sender=Payroll)
# def sync_payroll_to_ledger(sender, instance, created, **kwargs):
#     if created:
#         try:
#             entity = AccountingEntity.objects.get(organization=instance.worker.organization)
#             ledger = LedgerModel.objects.get_or_create(entity=entity, name=f"{entity.organization.name} General Ledger")[0]
            
#             journal_entry = JournalEntryModel.objects.create(
#                 ledger=ledger,
#                 description=f"Payroll for {instance.worker.user.username} - {instance.period}",
#                 timestamp=instance.created_at,
#                 entity=entity
#             )
            
#             expense_account = entity.get_coa_account(code='6000')  # Example: Payroll expense
#             cash_account = entity.get_coa_account(code='1000')     # Example: Cash
            
#             transactions = [
#                 {'account': expense_account, 'amount': instance.total, 'tx_type': TransactionModel.TX_TYPE_DEBIT},
#                 {'account': cash_account, 'amount': instance.total, 'tx_type': TransactionModel.TX_TYPE_CREDIT}
#             ]
#             journal_entry.post(transactions=transactions)
            
#             from spending_management.models import Expense
#             expense = Expense.objects.get(payroll_reference=instance)
#             expense.ledger_entry = journal_entry
#             expense.save()
            
#             from ticketing.utils import send_automatic_notification
#             send_automatic_notification(
#                 users=entity.organization.users.filter(rolepermissions__permission='manage_organization'),
#                 message=f"Payroll for {instance.worker.user.username} (${instance.total}) posted to ledger."
#             )
#         except ObjectDoesNotExist:
#             pass

# @receiver(post_save, sender=CorporateCard)
# def sync_card_creation_to_ledger(sender, instance, created, **kwargs):
#     if created:
#         try:
#             entity = AccountingEntity.objects.get(organization=instance.organization)
#             ledger = LedgerModel.objects.get_or_create(entity=entity, name=f"{entity.organization.name} General Ledger")[0]
            
#             journal_entry = JournalEntryModel.objects.create(
#                 ledger=ledger,
#                 description=f"Corporate Card Issued to {instance.holder.user.username}",
#                 timestamp=instance.created_at,
#                 entity=entity
#             )
            
#             liability_account = entity.get_coa_account(code='2000')  # Example: Card liability
#             cash_account = entity.get_coa_account(code='1000')       # Example: Cash
            
#             transactions = [
#                 {'account': liability_account, 'amount': instance.spending_limit, 'tx_type': TransactionModel.TX_TYPE_CREDIT},
#                 {'account': cash_account, 'amount': instance.spending_limit, 'tx_type': TransactionModel.TX_TYPE_DEBIT}
#             ]
#             journal_entry.post(transactions=transactions)
            
#             from ticketing.utils import send_automatic_notification
#             send_automatic_notification(
#                 users=entity.organization.users.filter(rolepermissions__permission='manage_organization'),
#                 message=f"Corporate card (ending {instance.card_number[-4:]}) with limit ${instance.spending_limit} issued and posted to ledger."
#             )
#         except ObjectDoesNotExist:
#             pass
# accounting/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_ledger.models import LedgerModel, JournalEntryModel, TransactionModel
from spending_management.models import Expense, CorporateCard
from payroll_benefits.models import Payroll
from .models import AccountingEntity
from django.core.exceptions import ObjectDoesNotExist

@receiver(post_save, sender=Expense)
def sync_expense_to_ledger(sender, instance, created, **kwargs):
    if instance.status == 'approved' and not hasattr(instance, 'ledger_entry'):
        try:
            entity = AccountingEntity.objects.get(organization=instance.organization)
            ledger = LedgerModel.objects.get_or_create(entity=entity, name=f"{entity.organization.name} General Ledger")[0]
            
            journal_entry = JournalEntryModel.objects.create(
                ledger=ledger,
                description=instance.description,
                timestamp=instance.created_at,
                entity=entity
            )
            
            # Simplified accounts (configure these in Django Ledger)
            expense_account = entity.get_coa_account(code='6000')  # Example: Expense account
            cash_account = entity.get_coa_account(code='1000')     # Example: Cash account
            liability_account = entity.get_coa_account(code='2000') # Example: Card liability
            
            transactions = [
                {'account': expense_account, 'amount': instance.amount, 'tx_type': TransactionModel.TX_TYPE_DEBIT},
                {'account': cash_account if not instance.card else liability_account, 
                 'amount': instance.amount, 'tx_type': TransactionModel.TX_TYPE_CREDIT}
            ]
            journal_entry.post(transactions=transactions)
            
            instance.ledger_entry = journal_entry
            instance.save()
            
            from ticketing.utils import send_automatic_notification
            org_admins = entity.organization.users.filter(custom_role__permissions__contains=['manage_organization'])
            send_automatic_notification(
                users=org_admins,
                message=f"Expense '{instance.description}' (${instance.amount}) posted to ledger."
            )
        except ObjectDoesNotExist:
            pass  # Handle missing entity/ledger gracefully

@receiver(post_save, sender=Payroll)
def sync_payroll_to_ledger(sender, instance, created, **kwargs):
    if created:
        try:
            entity = AccountingEntity.objects.get(organization=instance.worker.organization)
            ledger = LedgerModel.objects.get_or_create(entity=entity, name=f"{entity.organization.name} General Ledger")[0]
            
            journal_entry = JournalEntryModel.objects.create(
                ledger=ledger,
                description=f"Payroll for {instance.worker.user.username} - {instance.period}",
                timestamp=instance.created_at,
                entity=entity
            )
            
            expense_account = entity.get_coa_account(code='6000')  # Example: Payroll expense
            cash_account = entity.get_coa_account(code='1000')     # Example: Cash
            
            transactions = [
                {'account': expense_account, 'amount': instance.total, 'tx_type': TransactionModel.TX_TYPE_DEBIT},
                {'account': cash_account, 'amount': instance.total, 'tx_type': TransactionModel.TX_TYPE_CREDIT}
            ]
            journal_entry.post(transactions=transactions)
            
            from spending_management.models import Expense
            expense = Expense.objects.get(payroll_reference=instance)
            expense.ledger_entry = journal_entry
            expense.save()
            
            from ticketing.utils import send_automatic_notification
            org_admins = entity.organization.users.filter(custom_role__permissions__contains=['manage_organization'])
            send_automatic_notification(
                users=org_admins,
                message=f"Payroll for {instance.worker.user.username} (${instance.total}) posted to ledger."
            )
        except ObjectDoesNotExist:
            pass

@receiver(post_save, sender=CorporateCard)
def sync_card_creation_to_ledger(sender, instance, created, **kwargs):
    if created:
        try:
            entity = AccountingEntity.objects.get(organization=instance.organization)
            ledger = LedgerModel.objects.get_or_create(entity=entity, name=f"{entity.organization.name} General Ledger")[0]
            
            journal_entry = JournalEntryModel.objects.create(
                ledger=ledger,
                description=f"Corporate Card Issued to {instance.holder.user.username}",
                timestamp=instance.created_at,
                entity=entity
            )
            
            liability_account = entity.get_coa_account(code='2000')  # Example: Card liability
            cash_account = entity.get_coa_account(code='1000')       # Example: Cash
            
            transactions = [
                {'account': liability_account, 'amount': instance.spending_limit, 'tx_type': TransactionModel.TX_TYPE_CREDIT},
                {'account': cash_account, 'amount': instance.spending_limit, 'tx_type': TransactionModel.TX_TYPE_DEBIT}
            ]
            journal_entry.post(transactions=transactions)
            
            from ticketing.utils import send_automatic_notification
            org_admins = entity.organization.users.filter(custom_role__permissions__contains=['manage_organization'])
            send_automatic_notification(
                users=org_admins,
                message=f"Corporate card (ending {instance.card_number[-4:]}) with limit ${instance.spending_limit} issued and posted to ledger."
            )
        except ObjectDoesNotExist:
            pass