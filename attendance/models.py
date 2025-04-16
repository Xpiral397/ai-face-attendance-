from django.db import models
import uuid

class AttendanceRecord(models.Model):
    """Attendance record model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name='attendance_records')
    course = models.ForeignKey('academic.Course', on_delete=models.CASCADE, related_name='attendance_records')
    timestamp = models.DateTimeField(auto_now_add=True)
    verified_by_face = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user', 'course', 'timestamp']
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.course.code} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}" 