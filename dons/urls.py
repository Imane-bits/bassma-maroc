from django.urls import path

from . import views

app_name = "dons"
urlpatterns = [
    path("nouveau/", views.creer_don, name="creer_don"),
    path("mes-dons/", views.mes_dons, name="mes_dons"),
    path("responsable/dons/", views.liste_dons_a_affecter, name="liste_dons"),
    path(
        "responsable/affectations/nouvelle/",
        views.creer_affectation,
        name="creer_affectation",
    ),
]
