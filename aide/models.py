from django.conf import settings
from django.db import models


class Beneficiaire(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profil_beneficiaire"
    )
    situation_familiale = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return str(self.user)


class DemandeAide(models.Model):
    class Urgence(models.TextChoices):
        FAIBLE = "faible", "Faible"
        MOYENNE = "moyenne", "Moyenne"
        HAUTE = "haute", "Haute"

    class Statut(models.TextChoices):
        EN_ATTENTE = "en_attente", "En attente"
        EN_COURS = "en_cours", "En cours"
        ACCEPTEE = "acceptee", "Acceptée"
        REFUSEE = "refusee", "Refusée"

    beneficiaire = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="demandes_aide"
    )
    description = models.TextField()
    urgence = models.CharField(max_length=10, choices=Urgence.choices)
    statut = models.CharField(
        max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE
    )
    date_soumission = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Demande #{self.pk} ({self.statut})"


class PieceJustificative(models.Model):
    demande = models.ForeignKey(
        DemandeAide, on_delete=models.CASCADE, related_name="pieces"
    )
    fichier = models.FileField(upload_to="pieces_justificatives/%Y/%m/")
    date_ajout = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.fichier.name
