from django.urls import path, re_path
from .views import RouteListCreateView, BusRouteView, update_route

urlpatterns = [
    path("", RouteListCreateView.as_view()),      # /api/routes/
    re_path(r'^(?P<bus_no>\w+)/?$', BusRouteView.as_view()),  # Matches '100' or '100/'
    path("<int:route_id>/", update_route),       
]
