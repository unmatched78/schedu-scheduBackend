# spending_management/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('categories/', SpendingCategoryListCreateAPIView.as_view(), name='list-create-categories'),
    path('budgets/', BudgetListCreateAPIView.as_view(), name='list-create-budgets'),
    path('budgets/<int:pk>/approve/', BudgetApprovalAPIView.as_view(), name='approve-budget'),
    path('allocations/', BudgetAllocationListCreateAPIView.as_view(), name='list-create-allocations'),
    path('cards/', CorporateCardListCreateAPIView.as_view(), name='list-create-cards'),
    path('expenses/', ExpenseListCreateAPIView.as_view(), name='list-create-expenses'),
    path('expenses/<int:pk>/approve/', ExpenseApprovalAPIView.as_view(), name='approve-expense'),
    path('report/', SpendingReportAPIView.as_view(), name='spending-report'),
]