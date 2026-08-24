from django.urls import path

from . import views

app_name = "formation"
urlpatterns = [
    path("", views.liste_formations, name="liste_formations"),
    path("inscription/", views.inscription_formation, name="inscription_formation"),
    path(
        "confirmation/<str:numero_inscription>/",
        views.confirmation,
        name="confirmation",
    ),
    path("suivi/", views.suivi_formation, name="suivi_formation"),
]
