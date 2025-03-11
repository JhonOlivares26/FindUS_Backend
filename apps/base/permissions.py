from rest_framework import permissions


class IsOrganizerUser(permissions.BasePermission):
    message = "Solo los organizadores pueden realizar esta acción."

    def has_permission(self, request, view):
        return request.user.user_type == "3"  # "3" es el valor para ORGANIZER


class IsCustomerUser(permissions.BasePermission):
    message = "Solo los usuarios pueden realizar esta acción."

    def has_permission(self, request, view):
        return request.user.user_type == "1"  # "1" es el valor para CUSTOMER
