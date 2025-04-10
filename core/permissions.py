# core/permissions.py
from django.core.exceptions import PermissionDenied
from .models import CustomUser, CustomRole

AVAILABLE_PERMISSIONS = [
    # Core App
    'manage_all',               # Superuser-level access to everything
    'manage_organization',      # Full org management (roles, users, settings)
    'view_organization_details',# View org details without edit
    'create_roles',             # Create custom roles
    'edit_roles',               # Edit existing roles
    'delete_roles',             # Delete roles
    'assign_roles',             # Assign roles to users
    'view_users',               # View all users in org
    'create_users',             # Add new users
    'edit_users',               # Edit user details
    'delete_users',             # Remove users
    'create_organization',      # Create new organizations

    # Scheduling App
    'create_departments',       # Create new departments
    'edit_department',          # Edit department details
    'delete_department',        # Delete departments
    'view_department_details',  # View department info
    'assign_department_head',   # Assign a head to a department
    'schedule_shifts',          # Create/edit shift schedules
    'view_department_shifts',   # View shifts for a department
    'view_all_shifts',          # View shifts across all departments
    'work_shifts',              # Work assigned shifts (e.g., clock in/out)
    'request_swap',             # Request shift swaps
    'approve_swap',             # Approve/deny shift swaps

    # HR App
    'create_employee_profiles', # Create new employee profiles
    'edit_employee_profiles',   # Edit employee profiles
    'delete_employee_profiles', # Delete employee profiles
    'view_employee_profiles',   # View employee profiles
    'track_attendance',         # Record attendance
    'view_attendance',          # View attendance records
    'create_performance_reviews',# Create performance reviews
    'edit_performance_reviews', # Edit performance reviews
    'view_performance_reviews', # View performance reviews
    'create_goals',             # Set goals for workers
    'edit_goals',               # Edit goals
    'view_goals',               # View goals
    'create_leave_requests',    # Submit leave requests
    'view_leave_requests',      # View own leave requests
    'approve_leave_requests',   # Approve/deny leave requests
    'view_all_leave_requests',  # View all leave requests in dept/org
    'create_company_policies',  # Create company policies
    'edit_company_policies',    # Edit company policies
    'view_company_policies',    # View company policies
    'view_payslips',            # View own payslips

    # Payroll and Benefits App
    'generate_payroll',         # Generate payroll for workers
    'approve_payroll',          # Approve payroll before processing
    'view_payroll_details',     # View payroll details (own or all)
    'edit_payroll_settings',    # Edit payroll settings (base salary, bonuses)
    'view_payroll_reports',     # View payroll reports
    'create_benefits',          # Create new benefits
    'edit_benefits',            # Edit existing benefits
    'delete_benefits',          # Delete benefits
    'view_benefits',            # View available benefits
    'enroll_in_benefits',       # Enroll in benefits as a worker

    # Compliance and Legal App
    'create_compliance_requirements', # Create compliance tasks
    'edit_compliance_requirements',   # Edit compliance tasks
    'view_compliance_requirements',   # View compliance tasks (own or all)
    'update_compliance_status',       # Update compliance status
    'view_compliance_reports',        # View compliance status reports
    'create_legal_documents',         # Upload legal documents
    'edit_legal_documents',           # Edit legal documents
    'view_legal_documents',           # View legal documents
    'view_audit_logs',                # View audit logs

    # Spending Management App
    'create_spending_categories',     # Create spending categories
    'edit_spending_categories',       # Edit spending categories
    'view_spending_categories',       # View spending categories
    'create_budgets',                 # Create budgets
    'edit_budgets',                   # Edit budgets
    'approve_budgets',                # Approve/reject budgets
    'view_budgets',                   # View budgets
    'create_budget_allocations',      # Allocate budget to categories
    'edit_budget_allocations',        # Edit allocations
    'view_budget_allocations',        # View allocations
    'create_corporate_cards',         # Issue corporate cards
    'edit_corporate_cards',           # Edit card details (e.g., limits)
    'view_corporate_cards',           # View card details
    'create_expenses',                # Submit expenses
    'edit_expenses',                  # Edit pending expenses
    'approve_expenses',               # Approve/reject expenses
    'view_expenses',                  # View expenses (own or all)
    'view_spending_reports',          # View spending reports

    # Accounting App
    'create_accounting_entities',     # Create accounting entities
    'edit_accounting_entities',       # Edit accounting entities
    'view_accounting_entities',       # View accounting entities
    'generate_ledger_reports',        # Generate balance sheets, income statements
    'view_ledger_reports',            # View ledger reports
    'create_report_settings',         # Create report settings
    'edit_report_settings',           # Edit report settings
    'view_report_settings',           # View report settings

    # Ticketing App
    'create_tickets',           # Submit tickets
    'edit_tickets',             # Edit tickets
    'assign_tickets',           # Assign tickets to users
    'resolve_tickets',          # Resolve tickets
    'view_tickets',             # View tickets (own or all)
    'send_notifications',       # Send manual notifications
    'view_notifications',       # View received notifications
]

def has_permission(user: CustomUser, permission: str) -> bool:
    """
    Check if the user has the specified permission based on their custom_role.
    """
    if not user.is_authenticated:
        return False
    if not user.custom_role:
        return False
    return permission in user.custom_role.permissions

def has_role(user: CustomUser, role_name: str) -> bool:
    """
    Check if the user has the specified role.
    """
    if not user.is_authenticated:
        return False
    return user.custom_role and user.custom_role.name == role_name

def require_permission(permission: str):
    """
    Decorator to enforce a permission check before executing a view or function.
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if not has_permission(self.request.user, permission):
                raise PermissionDenied(f"Permission '{permission}' required.")
            return func(self, *args, **kwargs)
        return wrapper
    return decorator

def require_any_permission(permissions: list):
    """
    Decorator to enforce that at least one of the listed permissions is present.
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if not any(has_permission(self.request.user, perm) for perm in permissions):
                raise PermissionDenied(f"One of {permissions} required.")
            return func(self, *args, **kwargs)
        return wrapper
    return decorator

def get_user_permissions(user: CustomUser) -> list:
    """
    Get all permissions for a user based on their custom_role.
    """
    return user.custom_role.permissions if user.custom_role else []

def get_available_permissions(organization=None) -> list:
    """
    Get all unique permissions available for role creation.
    Could be filtered by organization-specific rules later.
    """
    return AVAILABLE_PERMISSIONS