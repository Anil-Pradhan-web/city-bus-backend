from django.urls import path
from .views import RouteListCreateView, BusRouteView

urlpatterns = [
    path("", RouteListCreateView.as_view()),      # /api/routes/
    path("<int:bus_no>/", BusRouteView.as_view()),  # /api/routes/300/
]
