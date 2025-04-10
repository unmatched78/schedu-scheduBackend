# # spending_management/views.py
# from rest_framework import generics, status
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from django.core.exceptions import PermissionDenied
# from .models import SpendingCategory, Budget, BudgetAllocation, CorporateCard, Expense
# from .serializers import SpendingCategorySerializer, BudgetSerializer, BudgetAllocationSerializer, CorporateCardSerializer, ExpenseSerializer
# from rolepermissions.checkers import has_permission
# from core.models import Worker, CustomUser
# from ticketing.utils import send_automatic_notification
# from django.utils import timezone

# class SpendingCategoryListCreateAPIView(generics.ListCreateAPIView):
#     serializer_class = SpendingCategorySerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return SpendingCategory.objects.filter(organization=self.request.user.organization)

#     def perform_create(self, serializer):
#         if not has_permission(self.request.user, 'manage_organization'):
#             raise PermissionDenied("Permission denied.")
#         category = serializer.save(organization=self.request.user.organization)
#         send_automatic_notification(
#             users=CustomUser.objects.filter(organization=self.request.user.organization, rolepermissions__permission='manage_organization'),
#             message=f"New spending category '{category.name}' ({category.category_type}) with max limit ${category.max_limit or 'N/A'} added by {self.request.user.username}."
#         )

# class BudgetListCreateAPIView(generics.ListCreateAPIView):
#     serializer_class = BudgetSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return Budget.objects.filter(organization=self.request.user.organization)

#     def perform_create(self, serializer):
#         if not has_permission(self.request.user, 'manage_organization'):
#             raise PermissionDenied("Permission denied.")
#         budget = serializer.save(organization=self.request.user.organization, status='pending_approval')
#         send_automatic_notification(
#             users=CustomUser.objects.filter(organization=self.request.user.organization, rolepermissions__permission='manage_organization').exclude(id=self.request.user.id),
#             message=f"New budget '{budget.name}' (${budget.total_amount}) pending approval, created by {self.request.user.username}."
#         )

# class BudgetApprovalAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, pk):
#         if not has_permission(self.request.user, 'manage_organization'):
#             raise PermissionDenied("Permission denied.")
#         budget = Budget.objects.get(pk=pk, organization=self.request.user.organization)
#         action = request.data.get('action')  # 'approve' or 'reject'
#         if action == 'approve':
#             budget.status = 'approved'
#             budget.approved_by = self.request.user
#             message = f"Budget '{budget.name}' approved by {self.request.user.username}."
#         elif action == 'reject':
#             budget.status = 'rejected'
#             message = f"Budget '{budget.name}' rejected by {self.request.user.username}."
#         else:
#             return Response({"error": "Invalid action."}, status=400)
#         budget.save()
#         send_automatic_notification(
#             users=CustomUser.objects.filter(organization=self.request.user.organization, rolepermissions__permission='manage_organization'),
#             message=message
#         )
#         return Response(BudgetSerializer(budget).data, status=200)

# class BudgetAllocationListCreateAPIView(generics.ListCreateAPIView):
#     serializer_class = BudgetAllocationSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return BudgetAllocation.objects.filter(budget__organization=self.request.user.organization)

#     def perform_create(self, serializer):
#         if not has_permission(self.request.user, 'manage_organization'):
#             raise PermissionDenied("Permission denied.")
#         budget = serializer.validated_data['budget']
#         if budget.status != 'approved':
#             raise PermissionDenied("Cannot allocate to unapproved budget.")
#         allocation = serializer.save()
#         send_automatic_notification(
#             users=CustomUser.objects.filter(organization=self.request.user.organization, rolepermissions__permission='manage_organization'),
#             message=f"Budget allocation of ${allocation.allocated_amount} to {allocation.category.name} added by {self.request.user.username}."
#         )

# class CorporateCardListCreateAPIView(generics.ListCreateAPIView):
#     serializer_class = CorporateCardSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return CorporateCard.objects.filter(organization=self.request.user.organization)

#     def perform_create(self, serializer):
#         if not has_permission(self.request.user, 'manage_organization'):
#             raise PermissionDenied("Permission denied.")
#         card = serializer.save(organization=self.request.user.organization)
#         send_automatic_notification(
#             users=[card.holder.user],
#             message=f"You’ve been issued a corporate card (ending {card.card_number[-4:]}) with a limit of ${card.spending_limit} by {self.request.user.username}."
#         )

# class ExpenseListCreateAPIView(generics.ListCreateAPIView):
#     serializer_class = ExpenseSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return Expense.objects.filter(organization=self.request.user.organization)

#     def perform_create(self, serializer):
#         category = serializer.validated_data['category']
#         amount = serializer.validated_data['amount']
#         card = serializer.validated_data.get('card')
        
#         if card and (card.current_balance + amount > card.spending_limit):
#             raise PermissionDenied(f"Card balance (${card.current_balance + amount}) would exceed limit (${card.spending_limit}).")
#         if category.max_limit and amount > category.max_limit:
#             raise PermissionDenied(f"Expense (${amount}) exceeds category max limit (${category.max_limit}).")
        
#         status = 'pending' if category.requires_approval else 'approved'
#         expense = serializer.save(organization=self.request.user.organization, created_by=self.request.user, status=status)
        
#         if status == 'pending':
#             send_automatic_notification(
#                 users=CustomUser.objects.filter(organization=self.request.user.organization, rolepermissions__permission='manage_organization').exclude(id=self.request.user.id),
#                 message=f"New expense '${expense.description}' (${expense.amount}) pending approval, added by {self.request.user.username}."
#             )
#         else:
#             send_automatic_notification(
#                 users=CustomUser.objects.filter(organization=self.request.user.organization, rolepermissions__permission='manage_organization'),
#                 message=f"New expense '${expense.description}' (${expense.amount}) added and auto-approved by {self.request.user.username}."
#             )

# class ExpenseApprovalAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, pk):
#         if not has_permission(self.request.user, 'manage_organization'):
#             raise PermissionDenied("Permission denied.")
#         expense = Expense.objects.get(pk=pk, organization=self.request.user.organization)
#         action = request.data.get('action')  # 'approve' or 'reject'
#         if action == 'approve':
#             expense.status = 'approved'
#             expense.approved_by = self.request.user
#             message = f"Expense '{expense.description}' (${expense.amount}) approved by {self.request.user.username}."
#         elif action == 'reject':
#             expense.status = 'rejected'
#             message = f"Expense '{expense.description}' (${expense.amount}) rejected by {self.request.user.username}."
#         else:
#             return Response({"error": "Invalid action."}, status=400)
#         expense.save()
#         send_automatic_notification(
#             users=[expense.created_by],
#             message=message
#         )
#         return Response(ExpenseSerializer(expense).data, status=200)

# class SpendingReportAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         if not has_permission(request.user, 'manage_organization'):
#             return Response({"error": "Permission denied."}, status=403)
        
#         org = request.user.organization
#         budgets = Budget.objects.filter(organization=org, status='approved')
#         expenses = Expense.objects.filter(organization=org, status='approved')
#         cards = CorporateCard.objects.filter(organization=org)
        
#         report = {
#             "total_budget": float(sum(b.total_amount for b in budgets)),
#             "total_spent": float(sum(e.amount for e in expenses)),
#             "by_category": {},
#             "corporate_cards": {}
#         }
        
#         for category in SpendingCategory.objects.filter(organization=org):
#             category_expenses = expenses.filter(category=category)
#             category_allocations = BudgetAllocation.objects.filter(category=category, budget__organization=org)
#             report["by_category"][category.name] = {
#                 "spent": float(sum(e.amount for e in category_expenses)),
#                 "allocated": float(sum(a.allocated_amount for a in category_allocations)),
#                 "max_limit": float(category.max_limit) if category.max_limit else None
#             }
        
#         for card in cards:
#             card_expenses = expenses.filter(card=card)
#             report["corporate_cards"][card.card_number[-4:]] = {
#                 "limit": float(card.spending_limit),
#                 "balance": float(card.current_balance),
#                 "spent": float(sum(e.amount for e in card_expenses))
#             }
        
#         return Response(report, status=200)
# spending_management/views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import PermissionDenied
from .models import SpendingCategory, Budget, BudgetAllocation, CorporateCard, Expense
from .serializers import SpendingCategorySerializer, BudgetSerializer, BudgetAllocationSerializer, CorporateCardSerializer, ExpenseSerializer
from core.permissions import require_permission, has_permission
from core.models import Worker, CustomUser
from ticketing.utils import send_automatic_notification
from django.utils import timezone

class SpendingCategoryListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = SpendingCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if has_permission(self.request.user, 'view_spending_categories'):
            return SpendingCategory.objects.filter(organization=self.request.user.organization)
        return SpendingCategory.objects.none()

    @require_permission('create_spending_categories')
    def perform_create(self, serializer):
        category = serializer.save(organization=self.request.user.organization)
        org_admins = CustomUser.objects.filter(
            organization=self.request.user.organization,
            custom_role__permissions__contains=['manage_organization']
        )
        send_automatic_notification(
            users=org_admins,
            message=f"New spending category '{category.name}' ({category.category_type}) with max limit ${category.max_limit or 'N/A'} added by {self.request.user.username}."
        )

class BudgetListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if has_permission(self.request.user, 'view_budgets'):
            return Budget.objects.filter(organization=self.request.user.organization)
        return Budget.objects.none()

    @require_permission('create_budgets')
    def perform_create(self, serializer):
        budget = serializer.save(organization=self.request.user.organization, status='pending_approval')
        org_admins = CustomUser.objects.filter(
            organization=self.request.user.organization,
            custom_role__permissions__contains=['manage_organization']
        ).exclude(id=self.request.user.id)
        send_automatic_notification(
            users=org_admins,
            message=f"New budget '{budget.name}' (${budget.total_amount}) pending approval, created by {self.request.user.username}."
        )

class BudgetApprovalAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @require_permission('approve_budgets')
    def post(self, request, pk):
        budget = Budget.objects.get(pk=pk, organization=self.request.user.organization)
        action = request.data.get('action')  # 'approve' or 'reject'
        if action == 'approve':
            budget.status = 'approved'
            budget.approved_by = self.request.user
            message = f"Budget '{budget.name}' approved by {self.request.user.username}."
        elif action == 'reject':
            budget.status = 'rejected'
            message = f"Budget '{budget.name}' rejected by {self.request.user.username}."
        else:
            return Response({"error": "Invalid action."}, status=400)
        budget.save()
        org_admins = CustomUser.objects.filter(
            organization=self.request.user.organization,
            custom_role__permissions__contains=['manage_organization']
        )
        send_automatic_notification(
            users=org_admins,
            message=message
        )
        return Response(BudgetSerializer(budget).data, status=200)

class BudgetAllocationListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = BudgetAllocationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if has_permission(self.request.user, 'view_budget_allocations'):
            return BudgetAllocation.objects.filter(budget__organization=self.request.user.organization)
        return BudgetAllocation.objects.none()

    @require_permission('create_budget_allocations')
    def perform_create(self, serializer):
        budget = serializer.validated_data['budget']
        if budget.status != 'approved':
            raise PermissionDenied("Cannot allocate to unapproved budget.")
        allocation = serializer.save()
        org_admins = CustomUser.objects.filter(
            organization=self.request.user.organization,
            custom_role__permissions__contains=['manage_organization']
        )
        send_automatic_notification(
            users=org_admins,
            message=f"Budget allocation of ${allocation.allocated_amount} to {allocation.category.name} added by {self.request.user.username}."
        )

class CorporateCardListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CorporateCardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if has_permission(self.request.user, 'view_corporate_cards'):
            return CorporateCard.objects.filter(organization=self.request.user.organization)
        return CorporateCard.objects.none()

    @require_permission('create_corporate_cards')
    def perform_create(self, serializer):
        card = serializer.save(organization=self.request.user.organization)
        send_automatic_notification(
            users=[card.holder.user],
            message=f"You’ve been issued a corporate card (ending {card.card_number[-4:]}) with a limit of ${card.spending_limit} by {self.request.user.username}."
        )

class ExpenseListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if has_permission(self.request.user, 'view_expenses'):
            return Expense.objects.filter(organization=self.request.user.organization)
        return Expense.objects.filter(organization=self.request.user.organization, created_by=self.request.user)

    @require_permission('create_expenses')
    def perform_create(self, serializer):
        category = serializer.validated_data['category']
        amount = serializer.validated_data['amount']
        card = serializer.validated_data.get('card')

        if card and (card.current_balance + amount > card.spending_limit):
            raise PermissionDenied(f"Card balance (${card.current_balance + amount}) would exceed limit (${card.spending_limit}).")
        if category.max_limit and amount > category.max_limit:
            raise PermissionDenied(f"Expense (${amount}) exceeds category max limit (${category.max_limit}).")

        status = 'pending' if category.requires_approval else 'approved'
        expense = serializer.save(organization=self.request.user.organization, created_by=self.request.user, status=status)

        org_admins = CustomUser.objects.filter(
            organization=self.request.user.organization,
            custom_role__permissions__contains=['manage_organization']
        )
        if status == 'pending':
            send_automatic_notification(
                users=org_admins.exclude(id=self.request.user.id),
                message=f"New expense '{expense.description}' (${expense.amount}) pending approval, added by {self.request.user.username}."
            )
        else:
            send_automatic_notification(
                users=org_admins,
                message=f"New expense '{expense.description}' (${expense.amount}) added and auto-approved by {self.request.user.username}."
            )

class ExpenseApprovalAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @require_permission('approve_expenses')
    def post(self, request, pk):
        expense = Expense.objects.get(pk=pk, organization=self.request.user.organization)
        action = request.data.get('action')  # 'approve' or 'reject'
        if action == 'approve':
            expense.status = 'approved'
            expense.approved_by = self.request.user
            message = f"Expense '{expense.description}' (${expense.amount}) approved by {self.request.user.username}."
        elif action == 'reject':
            expense.status = 'rejected'
            message = f"Expense '{expense.description}' (${expense.amount}) rejected by {self.request.user.username}."
        else:
            return Response({"error": "Invalid action."}, status=400)
        expense.save()
        send_automatic_notification(
            users=[expense.created_by],
            message=message
        )
        return Response(ExpenseSerializer(expense).data, status=200)

class SpendingReportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @require_permission('view_spending_reports')
    def get(self, request):
        org = request.user.organization
        budgets = Budget.objects.filter(organization=org, status='approved')
        expenses = Expense.objects.filter(organization=org, status='approved')
        cards = CorporateCard.objects.filter(organization=org)

        report = {
            "total_budget": float(sum(b.total_amount for b in budgets)),
            "total_spent": float(sum(e.amount for e in expenses)),
            "by_category": {},
            "corporate_cards": {}
        }

        for category in SpendingCategory.objects.filter(organization=org):
            category_expenses = expenses.filter(category=category)
            category_allocations = BudgetAllocation.objects.filter(category=category, budget__organization=org)
            report["by_category"][category.name] = {
                "spent": float(sum(e.amount for e in category_expenses)),
                "allocated": float(sum(a.allocated_amount for a in category_allocations)),
                "max_limit": float(category.max_limit) if category.max_limit else None
            }

        for card in cards:
            card_expenses = expenses.filter(card=card)
            report["corporate_cards"][card.card_number[-4:]] = {
                "limit": float(card.spending_limit),
                "balance": float(card.current_balance),
                "spent": float(sum(e.amount for e in card_expenses))
            }

        return Response(report, status=200)