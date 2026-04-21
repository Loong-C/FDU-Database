from rest_framework.permissions import SAFE_METHODS, BasePermission


class RolePermission(BasePermission):
    read_roles: set[str] = set()
    write_roles: set[str] = set()
    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        role = getattr(user, "role", None)
        if request.method in SAFE_METHODS:
            return role in self.read_roles
        return role in self.write_roles


class AdminOnlyPermission(RolePermission):
    read_roles = {"admin"}
    write_roles = {"admin"}


class CatalogPermission(RolePermission):
    read_roles = {"admin", "operator"}
    write_roles = {"admin"}


class CustomerSalesPermission(RolePermission):
    read_roles = {"admin", "operator"}
    write_roles = {"admin", "operator"}


class AnalyticsPermission(RolePermission):
    read_roles = {"admin", "operator", "viewer"}
    write_roles = set()
