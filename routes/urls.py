from django.urls import path, re_path
from .views import RouteListCreateView, BusRouteView, update_route, TripPlannerView, SearchSuggestionsView

urlpatterns = [
    path("", RouteListCreateView.as_view()),      # /api/routes/
    path("plan/", TripPlannerView.as_view()),     # /api/routes/plan/?from=X&to=Y
    path("search/", SearchSuggestionsView.as_view()), # /api/routes/search/?q=...
    re_path(r'^(?P<bus_no>\w+)/?$', BusRouteView.as_view()),  # Matches '100' or '100/'
    path("<int:route_id>/", update_route),       
]
