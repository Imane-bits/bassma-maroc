from django.urls import path

from . import views

app_name = "dons"
urlpatterns = [
    path("nouveau/", views.creer_don, name="creer_don"),
    path("nouveau/merci/", views.merci_don, name="merci_don"),
    path("mes-dons/", views.mes_dons, name="mes_dons"),
    path("mes-dons/export/", views.exporter_mes_dons, name="exporter_mes_dons"),
    path("mes-dons/recu/", views.recu_fiscal, name="recu_fiscal"),
    path("responsable/dons/", views.liste_dons_a_affecter, name="liste_dons"),
    path("responsable/dons/<int:pk>/", views.don_detail, name="don_detail"),
    path(
        "responsable/affectations/nouvelle/",
        views.creer_affectation,
        name="creer_affectation",
    ),
]
