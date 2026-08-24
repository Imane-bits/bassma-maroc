from django.urls import path

from . import views

app_name = "comptabilite"
urlpatterns = [
    path("consolidation/", views.consolidation, name="consolidation"),
    path("bilan/", views.bilan_financier, name="bilan_financier"),
    path("export/", views.exporter_donnees, name="exporter_donnees"),
]
