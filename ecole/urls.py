from django.urls import path

from . import views

app_name = "ecole"
urlpatterns = [
    path("preinscription/", views.preinscrire, name="preinscrire"),
    path(
        "preinscription/confirmation/<str:numero_dossier>/",
        views.confirmation,
        name="confirmation",
    ),
    path("preinscription/suivi/", views.suivi_preinscription, name="suivi_preinscription"),
    path("responsable/paiements/", views.liste_paiements, name="liste_paiements"),
    path(
        "responsable/paiements/<int:pk>/payer/",
        views.marquer_paye,
        name="marquer_paye",
    ),
    path(
        "responsable/preinscriptions/",
        views.liste_preinscriptions,
        name="liste_preinscriptions",
    ),
    path(
        "responsable/preinscriptions/<int:pk>/accepter/",
        views.accepter_preinscription,
        name="accepter_preinscription",
    ),
    path(
        "responsable/preinscriptions/<int:pk>/refuser/",
        views.refuser_preinscription,
        name="refuser_preinscription",
    ),
]
