# # TODO Add permission classes
#         if wishlist.user != request.user:
#             return Response(
#                 {'error': 'Permission denied'}, 
#                 status=status.HTTP_403_FORBIDDEN
#                 )
from rest_framework.permissions import BasePermission


class IsAuthenticatedUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
class IsActiveUser(BasePermission):
    """
    Custom permission to allow access only to active users.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_active
class IsSuperUser(BasePermission):
    """
    Custom permission class to allow access only to superusers.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class IsVendor(BasePermission):
    """
    Permission class to check if the requesting user is a vendor.
    """

    def has_permission(self, request, view):
        print('requeset  is :',request.user)
        return request.user and request.user.is_vendor
    
class IsOwner(BasePermission):
    def has_object_permission(self, request, view):
        # Check if the requesting user is the owner of the object
        return request.booking.user == request.user

# from rest_framework import permissions
from rest_framework import permissions

class IsRoomOwner(BasePermission):
    """
    Custom permission to check if the requesting user is the creator of the room.  TODO Here is one mistake 
    """

    def has_object_permission(self, request, view):
        # Return True if the requesting user is the creator of the room
        return request.room.created_by == request.user
