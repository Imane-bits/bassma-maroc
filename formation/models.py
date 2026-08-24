import random

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class FormationCouture(models.Model):
    intitule = models.CharField(max_length=150)
    description = models.TextField()
    duree_semaines = models.PositiveIntegerField()

    def __str__(self):
        return self.intitule


def generer_numero_inscription():
    annee = timezone.now().year
    while True:
        candidat = f"INS-{annee}-{random.randint(0, 999999):06d}"
        if not InscriptionFormation.objects.filter(numero_inscription=candidat).exists():
            return candidat


def generer_numero_certification():
    annee = timezone.now().year
    while True:
        candidat = f"CERT-{annee}-{random.randint(0, 999999):06d}"
        if not Certification.objects.filter(numero=candidat).exists():
            return candidat


class InscriptionFormation(models.Model):
    class Statut(models.TextChoices):
        EN_COURS = "en_cours", _("قيد التكوين")
        TERMINEE = "terminee", _("منتهية")
        ABANDONNEE = "abandonnee", _("متوقفة")

    numero_inscription = models.CharField(max_length=20, unique=True, blank=True)
    beneficiaire = models.ForeignKey(
        "aide.Beneficiaire",
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

    def save(self, *args, **kwargs):
        if not self.numero_inscription:
            self.numero_inscription = generer_numero_inscription()
        super().save(*args, **kwargs)
        if self.statut == self.Statut.TERMINEE and not hasattr(self, "certification"):
            Certification.objects.create(
                inscription=self, numero=generer_numero_certification()
            )

    def __str__(self):
        return f"{self.numero_inscription} - {self.beneficiaire}"


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
