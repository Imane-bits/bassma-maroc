from django.urls import path

from . import views

app_name = "personnel"
urlpatterns = [
    path("", views.liste_membres, name="liste_membres"),
    path("nouveau/", views.creer_membre, name="creer_membre"),
    path("<int:pk>/modifier/", views.modifier_membre, name="modifier_membre"),
    path("<int:pk>/desactiver/", views.desactiver_membre, name="desactiver_membre"),
    path("<int:pk>/activer/", views.activer_membre, name="activer_membre"),
]
