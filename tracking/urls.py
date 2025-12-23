from django.urls import path
from .views import UpdateLocationView, CurrentLocationView
from .views import BusETAView
urlpatterns = [
    path('update/', UpdateLocationView.as_view()),
    path('current/<int:bus_id>/', CurrentLocationView.as_view()),
]

urlpatterns += [
    path('eta/<int:bus_id>/', BusETAView.as_view()),
]
