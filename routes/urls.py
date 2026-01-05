from django.urls import path
from .views import RouteListCreateView, BusRouteView, update_route

urlpatterns = [
    path("", RouteListCreateView.as_view()),      # /api/routes/ (GET, POST)
    path("<int:bus_no>/", BusRouteView.as_view()),  # /api/routes/300/ (GET) - pehle check karega
    path("<int:route_id>/", update_route),        # /api/routes/{id}/ (PUT, PATCH) - baad mein
]
