from rest_framework import serializers
from django.contrib.auth.models import User
from .models import FavoriteRoute
from routes.serializers import RouteSerializer

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user

class FavoriteRouteSerializer(serializers.ModelSerializer):
    route_details = RouteSerializer(source='route', read_only=True)
    
    class Meta:
        model = FavoriteRoute
        fields = ['id', 'route', 'route_details', 'created_at']
        read_only_fields = ['user']
