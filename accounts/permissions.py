from rest_framework import permissions 


class IsAdminUser(permissions.BasePermission):
    """
    Allows access only to Admin users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'ADMIN')

class isWarehouseStaff(permissions.BasePermission):
    """
    Allows access to Warehouse Staff and Admins.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and 
            request.user.role in ['WAREHOUSE', 'ADMIN']
        )
    
class IsSalesStaff(permissions.BasePermission):
    """
    Allows access to Sales Staff, Cashiers, and Admins.
    (Assuming sales and cashiers might share some frontend views)
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['SALES', 'CASHIER', 'ADMIN']
        )

