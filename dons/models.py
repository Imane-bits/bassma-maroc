from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Don(models.Model):
    class TypeDon(models.TextChoices):
        UNIQUE = "unique", _("لمرة واحدة")
        MENSUEL = "mensuel", _("شهري")

    class Statut(models.TextChoices):
        RECU = "recu", _("مستلم")
        EN_AFFECTATION = "en_affectation", _("قيد التوزيع")
        DISTRIBUE = "distribue", _("موزّع")

    donateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="dons"
    )
    montant = models.DecimalField(_("المبلغ"), max_digits=10, decimal_places=2)
    date_don = models.DateField(auto_now_add=True)
    type_don = models.CharField(_("نوع التبرّع"), max_length=10, choices=TypeDon.choices)
    statut = models.CharField(
        _("الحالة"), max_length=20, choices=Statut.choices, default=Statut.RECU
    )
    demande_aide = models.ForeignKey(
        "aide.DemandeAide",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dons_cibles",
        verbose_name=_("الحالة المدعومة"),
    )

    def __str__(self):
        return f"Don #{self.pk} - {self.montant} ({self.donateur})"


class Affectation(models.Model):
    class Cible(models.TextChoices):
        BENEFICIAIRE = "beneficiaire", _("مستفيد")
        ECOLE = "ecole", _("المدرسة")
        CENTRE_FORMATION = "centre_formation", _("مركز التكوين")

    don = models.ForeignKey(Don, on_delete=models.CASCADE, related_name="affectations")
    budget = models.ForeignKey(
        "comptabilite.Budget", on_delete=models.PROTECT, related_name="affectations"
    )
    montant_affecte = models.DecimalField(_("المبلغ الموزّع"), max_digits=10, decimal_places=2)
    date_affectation = models.DateField(auto_now_add=True)
    cible = models.CharField(_("الوجهة"), max_length=20, choices=Cible.choices)
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
                _("طلب المساعدة مطلوب عند اختيار وجهة «مستفيد».")
            )
        if self.cible != self.Cible.BENEFICIAIRE and self.demande_aide_id:
            raise ValidationError(
                _("لا يجب ربط طلب مساعدة بهذه الوجهة.")
            )

    def __str__(self):
        return f"Affectation #{self.pk} ({self.cible})"
