from django.db import models
from django.core.validators import EmailValidator, MinLengthValidator

class Feedback(models.Model):
    FEEDBACK_TYPES = [
        ('general', 'General Inquiry'),
        ('complaint', 'Complaint'),
        ('suggestion', 'Suggestion'),
        ('appreciation', 'Appreciation'),
        ('technical', 'Technical Issue'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    # User Information
    name = models.CharField(max_length=100, validators=[MinLengthValidator(2)])
    email = models.EmailField(validators=[EmailValidator()])
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    # Feedback Details
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES, default='general')
    subject = models.CharField(max_length=200)
    message = models.TextField(validators=[MinLengthValidator(10)])
    
    # Bus-related (optional)
    bus_number = models.CharField(max_length=10, blank=True, null=True)
    route_number = models.CharField(max_length=10, blank=True, null=True)
    
    # Status & Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_response = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedbacks'
    
    def __str__(self):
        return f"{self.name} - {self.feedback_type} - {self.created_at.strftime('%Y-%m-%d')}"


class ContactMessage(models.Model):
    # Contact Form Submissions
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    # Metadata
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
    
    def __str__(self):
        return f"{self.name} - {self.subject}"
