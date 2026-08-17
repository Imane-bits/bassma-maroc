from django.urls import path

from . import views

app_name = "ecole"
urlpatterns = [
    path("bientot-disponible/", views.bientot_disponible, name="bientot_disponible"),
    path("responsable/paiements/", views.liste_paiements, name="liste_paiements"),
    path(
        "responsable/paiements/<int:pk>/payer/",
        views.marquer_paye,
        name="marquer_paye",
    ),
]
