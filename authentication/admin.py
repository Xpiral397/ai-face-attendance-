from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User  # Removed StudentProfile, LecturerProfile

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'full_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'full_name')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser',
                                    'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    search_fields = ('username', 'email', 'full_name')

# Commented out for initial migration
# @admin.register(StudentProfile)
# class StudentProfileAdmin(admin.ModelAdmin):
#     list_display = ('user', 'matric_number', 'department', 'level')
#     list_filter = ('level', 'department')
#     search_fields = ('user__username', 'user__email', 'matric_number')
# 
# @admin.register(LecturerProfile)
# class LecturerProfileAdmin(admin.ModelAdmin):
#     list_display = ('user',)
#     filter_horizontal = ('departments', 'subjects') 