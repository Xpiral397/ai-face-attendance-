from django.contrib import admin
from .models import Faculty, Department, Course

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'faculty', 'created_at', 'updated_at')
    list_filter = ('faculty',)
    search_fields = ('name', 'faculty__name')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'department', 'credit_hours', 'lecturer')
    list_filter = ('department', 'credit_hours')
    search_fields = ('code', 'name', 'department__name')
    raw_id_fields = ('lecturer',) 