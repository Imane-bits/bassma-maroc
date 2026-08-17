from django.urls import path

from . import views

app_name = "aide"
urlpatterns = [
    path("demandes/nouvelle/", views.soumettre_demande, name="soumettre_demande"),
    path(
        "confirmation/<str:numero_dossier>/",
        views.confirmation,
        name="confirmation",
    ),
    path("suivi/", views.suivi_dossier, name="suivi_dossier"),
    path("demandes/<int:pk>/", views.demande_detail, name="demande_detail"),
    path("responsable/demandes/", views.liste_demandes, name="liste_demandes"),
    path(
        "responsable/demandes/<int:pk>/accepter/",
        views.accepter_demande,
        name="accepter_demande",
    ),
    path(
        "responsable/demandes/<int:pk>/refuser/",
        views.refuser_demande,
        name="refuser_demande",
    ),
]
