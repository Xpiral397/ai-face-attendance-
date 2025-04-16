from django.db import models
import uuid

class Faculty(models.Model):
    """Faculty model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Faculties"

class Department(models.Model):
    """Department model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='departments')
    levels = models.JSONField(default=list)  # Store as a list of integers
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.faculty.name}"
    
    class Meta:
        unique_together = ['name', 'faculty']

class Course(models.Model):
    """Course model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    levels = models.JSONField(default=list)  # Store as a list of integers
    credit_hours = models.PositiveIntegerField(default=3)
    lecturer = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='taught_courses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    class Meta:
        unique_together = ['code', 'department'] 