"""
Custom permissions for API endpoints
"""
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner
        return obj.user == request.user or obj.author == request.user


class IsAdOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission for ClassifiedAd objects
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the ad owner
        return obj.user == request.user


class IsPublisherOrClient(permissions.BasePermission):
    """
    Permission for chat rooms - only publisher or client can access
    """

    def has_object_permission(self, request, view, obj):
        # Check if user is publisher or client in the chat room
        if hasattr(obj, 'publisher') and hasattr(obj, 'client'):
            return request.user == obj.publisher or request.user == obj.client
        return False


class IsVerified(permissions.BasePermission):
    """
    Permission to check if user is verified
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_authenticated:
            return request.user.verification_status == 'verified'
        return False


class IsPremiumUser(permissions.BasePermission):
    """
    Permission to check if user has active premium subscription
    """

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.is_premium
        return False
