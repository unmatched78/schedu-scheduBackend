# # spending_management/serializers.py
# from rest_framework import serializers
# from .models import SpendingCategory, Budget, BudgetAllocation, CorporateCard, Expense

# class SpendingCategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SpendingCategory
#         fields = ['id', 'organization', 'name', 'category_type', 'description', 'max_limit', 'requires_approval', 'created_at']

# class BudgetSerializer(serializers.ModelSerializer):
#     approved_by_username = serializers.CharField(source='approved_by.username', read_only=True)
#     class Meta:
#         model = Budget
#         fields = ['id', 'organization', 'name', 'start_date', 'end_date', 'total_amount', 'status', 'approved_by', 'approved_by_username', 'created_at', 'updated_at']

# class BudgetAllocationSerializer(serializers.ModelSerializer):
#     category_name = serializers.CharField(source='category.name', read_only=True)
#     class Meta:
#         model = BudgetAllocation
#         fields = ['id', 'budget', 'category', 'category_name', 'allocated_amount', 'spent_amount', 'warning_threshold']

# class CorporateCardSerializer(serializers.ModelSerializer):
#     holder_username = serializers.CharField(source='holder.user.username', read_only=True)
#     class Meta:
#         model = CorporateCard
#         fields = ['id', 'organization', 'card_number', 'holder', 'holder_username', 'spending_limit', 'current_balance', 'issued_date', 'expiry_date', 'is_active', 'created_at']

# class ExpenseSerializer(serializers.ModelSerializer):
#     category_name = serializers.CharField(source='category.name', read_only=True)
#     budget_name = serializers.CharField(source='budget.name', read_only=True)
#     created_by_username = serializers.CharField(source='created_by.username', read_only=True)
#     approved_by_username = serializers.CharField(source='approved_by.username', read_only=True)
#     card_number = serializers.CharField(source='card.card_number', read_only=True)
#     class Meta:
#         model = Expense
#         fields = ['id', 'organization', 'category', 'category_name', 'budget', 'budget_name', 'description', 
#                   'amount', 'incurred_date', 'status', 'created_by', 'created_by_username', 'approved_by', 
#                   'approved_by_username', 'payroll_reference', 'card', 'card_number', 'created_at']
# spending_management/serializers.py
from rest_framework import serializers
from .models import SpendingCategory, Budget, BudgetAllocation, CorporateCard, Expense
from core.models import CustomUser, Worker

class SpendingCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SpendingCategory
        fields = ['id', 'organization', 'name', 'category_type', 'description', 'max_limit', 'requires_approval', 'created_at']

class BudgetSerializer(serializers.ModelSerializer):
    approved_by_username = serializers.CharField(source='approved_by.username', read_only=True)

    class Meta:
        model = Budget
        fields = ['id', 'organization', 'name', 'start_date', 'end_date', 'total_amount', 'status', 'approved_by', 'approved_by_username', 'created_at', 'updated_at']

    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("End date must be after start date.")
        return data

class BudgetAllocationSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = BudgetAllocation
        fields = ['id', 'budget', 'category', 'category_name', 'allocated_amount', 'spent_amount', 'warning_threshold']

    def validate(self, data):
        budget = data['budget']
        category = data['category']
        allocated_amount = data['allocated_amount']

        if budget.organization != category.organization:
            raise serializers.ValidationError("Budget and category must belong to the same organization.")
        if BudgetAllocation.objects.filter(budget=budget, category=category).exists():
            raise serializers.ValidationError("This budget already has an allocation for this category.")
        if allocated_amount > budget.total_amount:
            raise serializers.ValidationError("Allocated amount cannot exceed total budget amount.")
        return data

class CorporateCardSerializer(serializers.ModelSerializer):
    holder_username = serializers.CharField(source='holder.user.username', read_only=True)

    class Meta:
        model = CorporateCard
        fields = ['id', 'organization', 'card_number', 'holder', 'holder_username', 'spending_limit', 'current_balance', 'issued_date', 'expiry_date', 'is_active', 'created_at']

    def validate(self, data):
        if data['issued_date'] > data['expiry_date']:
            raise serializers.ValidationError("Expiry date must be after issued date.")
        if data['spending_limit'] <= 0:
            raise serializers.ValidationError("Spending limit must be positive.")
        return data

class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    budget_name = serializers.CharField(source='budget.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    approved_by_username = serializers.CharField(source='approved_by.username', read_only=True)
    card_number = serializers.CharField(source='card.card_number', read_only=True)

    class Meta:
        model = Expense
        fields = ['id', 'organization', 'category', 'category_name', 'budget', 'budget_name', 'description',
                  'amount', 'incurred_date', 'status', 'created_by', 'created_by_username', 'approved_by',
                  'approved_by_username', 'payroll_reference', 'card', 'card_number', 'created_at']

    def validate(self, data):
        if data['amount'] <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        if data.get('budget') and data['budget'].status != 'approved':
            raise serializers.ValidationError("Cannot assign expense to an unapproved budget.")
        return data