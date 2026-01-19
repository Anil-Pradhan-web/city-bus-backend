from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from django.conf import settings
from .models import Feedback, ContactMessage
from .serializers import (
    FeedbackSerializer, 
    ContactMessageSerializer,
    FeedbackListSerializer
)

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [AllowAny]  # Anyone can submit feedback
    
    def get_serializer_class(self):
        if self.action == 'list':
            return FeedbackListSerializer
        return FeedbackSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Optional: Send email notification to admin
        # self.send_feedback_notification(serializer.data)
        
        headers = self.get_success_headers(serializer.data)
        return Response({
            'success': True,
            'message': 'Thank you for your feedback! We will review it shortly.',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get feedback statistics"""
        total = Feedback.objects.count()
        pending = Feedback.objects.filter(status='pending').count()
        resolved = Feedback.objects.filter(status='resolved').count()
        
        by_type = {}
        for choice in Feedback.FEEDBACK_TYPES:
            by_type[choice[0]] = Feedback.objects.filter(feedback_type=choice[0]).count()
        
        return Response({
            'total': total,
            'pending': pending,
            'resolved': resolved,
            'by_type': by_type
        })
    
    def send_feedback_notification(self, feedback_data):
        """Send email notification when new feedback is received"""
        try:
            subject = f"New Feedback: {feedback_data.get('subject')}"
            message = f"""
            New feedback received from {feedback_data.get('name')}
            
            Type: {feedback_data.get('feedback_type')}
            Email: {feedback_data.get('email')}
            Phone: {feedback_data.get('phone', 'N/A')}
            
            Message:
            {feedback_data.get('message')}
            
            Bus Number: {feedback_data.get('bus_number', 'N/A')}
            Route Number: {feedback_data.get('route_number', 'N/A')}
            """
            
            # Configure your email settings in settings.py
            # send_mail(
            #     subject,
            #     message,
            #     settings.DEFAULT_FROM_EMAIL,
            #     [settings.ADMIN_EMAIL],
            #     fail_silently=True,
            # )
        except Exception as e:
            print(f"Failed to send email: {e}")


class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        return Response({
            'success': True,
            'message': 'Thank you for contacting us! We will get back to you soon.',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a contact message as read"""
        message = self.get_object()
        message.is_read = True
        message.save()
        return Response({'success': True, 'message': 'Marked as read'})
