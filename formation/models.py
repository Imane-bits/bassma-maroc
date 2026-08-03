from django.conf import settings
from django.db import models


class FormationCouture(models.Model):
    intitule = models.CharField(max_length=150)
    description = models.TextField()
    duree_semaines = models.PositiveIntegerField()

    def __str__(self):
        return self.intitule


class InscriptionFormation(models.Model):
    class Statut(models.TextChoices):
        EN_COURS = "en_cours", "En cours"
        TERMINEE = "terminee", "Terminée"
        ABANDONNEE = "abandonnee", "Abandonnée"

    beneficiaire = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="inscriptions_formation",
    )
    formation = models.ForeignKey(
        FormationCouture, on_delete=models.CASCADE, related_name="inscriptions"
    )
    date_inscription = models.DateField(auto_now_add=True)
    progression = models.PositiveSmallIntegerField(default=0)
    statut = models.CharField(
        max_length=20, choices=Statut.choices, default=Statut.EN_COURS
    )

    def __str__(self):
        return f"{self.beneficiaire} - {self.formation}"


class Presence(models.Model):
    inscription = models.ForeignKey(
        InscriptionFormation, on_delete=models.CASCADE, related_name="presences"
    )
    date = models.DateField()
    present = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.inscription} - {self.date}"


class Certification(models.Model):
    inscription = models.OneToOneField(
        InscriptionFormation, on_delete=models.CASCADE, related_name="certification"
    )
    date_delivrance = models.DateField(auto_now_add=True)
    numero = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.numero
