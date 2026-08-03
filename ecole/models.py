from django.conf import settings
from django.db import models


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
