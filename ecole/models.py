import random

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Enseignant(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profil_enseignant"
    )
    matiere_niveau = models.CharField(max_length=100)
    planning = models.TextField(blank=True)

    def __str__(self):
        return str(self.user)


class Eleve(models.Model):
    tuteur = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="eleve"
    )
    enseignants = models.ManyToManyField(Enseignant, related_name="eleves", blank=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    classe = models.CharField(max_length=50)
    tuteur_nom = models.CharField(max_length=100)
    tuteur_contact = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.prenom} {self.nom}"


class PaiementScolarite(models.Model):
    class StatutPaiement(models.TextChoices):
        DU = "du", "Dû"
        PAYE = "paye", "Payé"
        EN_RETARD = "en_retard", "En retard"

    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE, related_name="paiements")
    budget = models.ForeignKey(
        "comptabilite.Budget", on_delete=models.PROTECT, related_name="paiements_scolarite"
    )
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_echeance = models.DateField()
    statut_paiement = models.CharField(
        max_length=20, choices=StatutPaiement.choices, default=StatutPaiement.DU
    )

    def __str__(self):
        return f"Paiement #{self.pk} - {self.eleve}"


def generer_numero_preinscription():
    annee = timezone.now().year
    while True:
        candidat = f"PRE-{annee}-{random.randint(0, 999999):06d}"
        if not PreinscriptionEleve.objects.filter(numero_dossier=candidat).exists():
            return candidat


class PreinscriptionEleve(models.Model):
    class Statut(models.TextChoices):
        EN_ATTENTE = "en_attente", _("قيد الانتظار")
        ACCEPTEE = "acceptee", _("مقبولة")
        REFUSEE = "refusee", _("مرفوضة")

    numero_dossier = models.CharField(max_length=20, unique=True, blank=True)
    nom_enfant = models.CharField(_("اسم العائلة"), max_length=100)
    prenom_enfant = models.CharField(_("الاسم الشخصي"), max_length=100)
    date_naissance = models.DateField(_("تاريخ الازدياد"))
    tuteur_nom = models.CharField(_("اسم الولي"), max_length=100)
    tuteur_contact = models.CharField(_("هاتف الولي"), max_length=100)
    adresse = models.TextField(_("العنوان"), blank=True)
    statut = models.CharField(
        max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE
    )
    date_soumission = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.numero_dossier:
            self.numero_dossier = generer_numero_preinscription()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.numero_dossier} - {self.prenom_enfant} {self.nom_enfant}"
