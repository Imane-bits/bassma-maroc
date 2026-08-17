from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Don(models.Model):
    class TypeDon(models.TextChoices):
        UNIQUE = "unique", _("Unique")
        MENSUEL = "mensuel", _("Mensuel")

    class Statut(models.TextChoices):
        RECU = "recu", _("Reçu")
        EN_AFFECTATION = "en_affectation", _("En affectation")
        DISTRIBUE = "distribue", _("Distribué")

    donateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="dons"
    )
    montant = models.DecimalField(_("montant"), max_digits=10, decimal_places=2)
    date_don = models.DateField(auto_now_add=True)
    type_don = models.CharField(_("type de don"), max_length=10, choices=TypeDon.choices)
    statut = models.CharField(
        _("statut"), max_length=20, choices=Statut.choices, default=Statut.RECU
    )

    def __str__(self):
        return f"Don #{self.pk} - {self.montant} ({self.donateur})"


class Affectation(models.Model):
    class Cible(models.TextChoices):
        BENEFICIAIRE = "beneficiaire", _("Bénéficiaire")
        ECOLE = "ecole", _("École")
        CENTRE_FORMATION = "centre_formation", _("Centre de formation")

    don = models.ForeignKey(Don, on_delete=models.CASCADE, related_name="affectations")
    budget = models.ForeignKey(
        "comptabilite.Budget", on_delete=models.PROTECT, related_name="affectations"
    )
    montant_affecte = models.DecimalField(_("montant affecté"), max_digits=10, decimal_places=2)
    date_affectation = models.DateField(auto_now_add=True)
    cible = models.CharField(_("cible"), max_length=20, choices=Cible.choices)
    demande_aide = models.ForeignKey(
        "aide.DemandeAide",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="affectations",
    )
    validee_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="affectations_validees",
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(cible="beneficiaire", demande_aide__isnull=False)
                    | (~models.Q(cible="beneficiaire") & models.Q(demande_aide__isnull=True))
                ),
                name="affectation_demande_aide_coherente",
            )
        ]

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.cible == self.Cible.BENEFICIAIRE and not self.demande_aide_id:
            raise ValidationError(
                _("Une demande d'aide est requise pour une affectation à un bénéficiaire.")
            )
        if self.cible != self.Cible.BENEFICIAIRE and self.demande_aide_id:
            raise ValidationError(
                _("Aucune demande d'aide ne doit être liée pour cette cible.")
            )

    def __str__(self):
        return f"Affectation #{self.pk} ({self.cible})"
