from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .models import FavoriteRoute
from .serializers import UserSerializer, FavoriteRouteSerializer
from rest_framework.permissions import IsAuthenticated

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class FavoriteRouteListCreateView(generics.ListCreateAPIView):
    serializer_class = FavoriteRouteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FavoriteRoute.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class FavoriteRouteDeleteView(generics.DestroyAPIView):
    serializer_class = FavoriteRouteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FavoriteRoute.objects.filter(user=self.request.user)
