from django.contrib.auth.models import AnonymousUser
from rest_framework.permissions import BasePermission


def get_user_role(user):
    if isinstance(user, AnonymousUser) or not user.is_authenticated:
        return None

    if user.groups.filter(name="teacher").exists():
        return "teacher"

    if user.groups.filter(name="student").exists():
        return "student"

    return None


class IsTeacherOrStudentUser(BasePermission):
    def has_permission(self, request, view):
        return get_user_role(request.user) in {"teacher", "student"}


class IsTeacherUser(BasePermission):
    def has_permission(self, request, view):
        return get_user_role(request.user) == "teacher"


class IsStudentUser(BasePermission):
    def has_permission(self, request, view):
        return get_user_role(request.user) == "student"
