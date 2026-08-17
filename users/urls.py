from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("inscription/", views.register, name="inscription"),
    path(
        "inscription/en-attente/",
        views.compte_en_attente,
        name="compte_en_attente",
    ),
    path(
        "connexion/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("deconnexion/", auth_views.LogoutView.as_view(), name="logout"),
    path("responsable/", views.espace_responsable, name="espace_responsable"),
    path(
        "responsable/comptes-en-attente/",
        views.comptes_en_attente,
        name="comptes_en_attente",
    ),
    path(
        "responsable/comptes-en-attente/<int:pk>/activer/",
        views.activer_compte,
        name="activer_compte",
    ),
    path(
        "mot-de-passe/reinitialiser/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html"
        ),
        name="password_reset",
    ),
    path(
        "mot-de-passe/reinitialiser/envoye/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "mot-de-passe/reinitialiser/confirmer/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "mot-de-passe/reinitialiser/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
