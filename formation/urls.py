from django.urls import path

from . import views

app_name = "formation"
urlpatterns = [
    path("bientot-disponible/", views.bientot_disponible, name="bientot_disponible"),
]
