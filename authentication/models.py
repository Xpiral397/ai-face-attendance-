from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid

class User(AbstractUser):
    """Custom User model"""
    
    class Role(models.TextChoices):
        STUDENT = 'student', _('Student')
        LECTURER = 'lecturer', _('Lecturer')
        ADMIN = 'admin', _('Admin')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)
    full_name = models.CharField(_('full name'), max_length=150, blank=True)
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
    )
    active = models.BooleanField(default=True)
    
    # Fields for face recognition would normally be here, but we're skipping for simplicity
    
    def __str__(self):
        return self.username

# Commented out for initial migration
# class StudentProfile(models.Model):
#     """Student profile information"""
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
#     department = models.ForeignKey('academic.Department', on_delete=models.CASCADE)
#     level = models.PositiveIntegerField()
#     matric_number = models.CharField(max_length=20, unique=True)
#     courses = models.ManyToManyField('academic.Course', blank=True)
#     
#     def __str__(self):
#         return f"{self.user.username} - {self.matric_number}"
# 
# class LecturerProfile(models.Model):
#     """Lecturer profile information"""
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='lecturer_profile')
#     departments = models.ManyToManyField('academic.Department')
#     levels = models.JSONField(default=list)  # Store as a list of integers
#     subjects = models.ManyToManyField('academic.Course', blank=True)
#     
#     def __str__(self):
#         return f"{self.user.username} - Lecturer" 