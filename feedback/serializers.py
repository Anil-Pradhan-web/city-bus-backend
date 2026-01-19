from rest_framework import serializers
from .models import Feedback, ContactMessage

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = [
            'id', 'name', 'email', 'phone', 'feedback_type', 
            'subject', 'message', 'bus_number', 'route_number',
            'status', 'admin_response', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'admin_response', 'created_at', 'updated_at']
    
    def validate_message(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters long.")
        return value
    
    def validate_email(self, value):
        if not '@' in value:
            raise serializers.ValidationError("Please enter a valid email address.")
        return value


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['id', 'name', 'email', 'phone', 'subject', 'message', 'is_read', 'created_at']
        read_only_fields = ['id', 'is_read', 'created_at']
    
    def validate_message(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters long.")
        return value


class FeedbackListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing feedbacks"""
    class Meta:
        model = Feedback
        fields = ['id', 'name', 'feedback_type', 'subject', 'status', 'created_at']
