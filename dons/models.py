from django.conf import settings
from django.db import models


class Don(models.Model):
    class TypeDon(models.TextChoices):
        UNIQUE = "unique", "Unique"
        MENSUEL = "mensuel", "Mensuel"

    class Statut(models.TextChoices):
        RECU = "recu", "Reçu"
        EN_AFFECTATION = "en_affectation", "En affectation"
        DISTRIBUE = "distribue", "Distribué"

    donateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="dons"
    )
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_don = models.DateField(auto_now_add=True)
    type_don = models.CharField(max_length=10, choices=TypeDon.choices)
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.RECU)

    def __str__(self):
        return f"Don #{self.pk} - {self.montant} ({self.donateur})"


class Affectation(models.Model):
    class Cible(models.TextChoices):
        BENEFICIAIRE = "beneficiaire", "Bénéficiaire"
        ECOLE = "ecole", "École"
        CENTRE_FORMATION = "centre_formation", "Centre de formation"

    don = models.ForeignKey(Don, on_delete=models.CASCADE, related_name="affectations")
    budget = models.ForeignKey(
        "comptabilite.Budget", on_delete=models.PROTECT, related_name="affectations"
    )
    montant_affecte = models.DecimalField(max_digits=10, decimal_places=2)
    date_affectation = models.DateField(auto_now_add=True)
    cible = models.CharField(max_length=20, choices=Cible.choices)

    def __str__(self):
        return f"Affectation #{self.pk} ({self.cible})"
