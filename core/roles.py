from rolepermissions.roles import AbstractUserRole

class MainAdmin(AbstractUserRole):
    available_permissions = {
        'manage_all': True,
    }

class OrganizationAdmin(AbstractUserRole):
    available_permissions = {
        'manage_organization': True,
    }

class DepartmentHead(AbstractUserRole):
    available_permissions = {
        'manage_department': True,
    }

class WorkerRole(AbstractUserRole):
    available_permissions = {
        'view_schedule': True,
        'suggest_edit': True,
    }
