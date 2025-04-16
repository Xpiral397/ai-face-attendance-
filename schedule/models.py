from django.db import models
import uuid

class TimeSlot(models.Model):
    """Time slot model"""
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    ]
    
    TYPE_CHOICES = [
        ('Physical', 'Physical'),
        ('Online', 'Online'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='Physical')
    
    def __str__(self):
        return f"{self.day} {self.start_time} - {self.end_time} ({self.type})"

class Schedule(models.Model):
    """Schedule model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lecturer = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name='schedules')
    course = models.ForeignKey('academic.Course', on_delete=models.CASCADE, related_name='schedules')
    department = models.ForeignKey('academic.Department', on_delete=models.CASCADE, related_name='schedules')
    level = models.PositiveIntegerField()
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name='schedules')
    room = models.CharField(max_length=50, blank=True, null=True)
    online_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.course.code} - {self.time_slot}"
    
    def clean(self):
        """Validate the schedule"""
        from django.core.exceptions import ValidationError
        
        # Ensure room is provided for physical class
        if self.time_slot.type == 'Physical' and not self.room:
            raise ValidationError("Room is required for physical classes")
        
        # Ensure online link is provided for online class
        if self.time_slot.type == 'Online' and not self.online_link:
            raise ValidationError("Online link is required for online classes")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs) 