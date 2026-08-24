from django.db import models
from django.utils.translation import gettext_lazy as _


class Budget(models.Model):
    class Module(models.TextChoices):
        ECOLE = "ecole", "École"
        CENTRE_FORMATION = "centre_formation", "Centre de formation"
        DONS = "dons", "Dons"
        GLOBAL = "global", "Global"

    module = models.CharField(max_length=20, choices=Module.choices)
    periode = models.CharField(max_length=20)
    recettes = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    depenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    @property
    def solde(self):
        return self.recettes - self.depenses

    def __str__(self):
        return f"Budget {self.module} - {self.periode}"


class DepenseMensuelle(models.Model):
    class Programme(models.TextChoices):
        AIDE = "aide", _("المساعدات الاجتماعية")
        ECOLE = "ecole", _("المدرسة والتعليم الأولي")
        FORMATION = "formation", _("مركز تكوين المرأة")
        ACTIVITES = "activites", _("الأنشطة والحملات")
        GESTION = "gestion", _("التسيير والإدارة")

    mois = models.DateField(_("الشهر"))
    programme = models.CharField(max_length=20, choices=Programme.choices)
    montant = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["mois", "programme"], name="unique_depense_mois_programme")
        ]
        ordering = ["mois"]

    def __str__(self):
        return f"{self.get_programme_display()} - {self.mois:%Y-%m}"


class RecetteMensuelle(models.Model):
    class Source(models.TextChoices):
        INDIVIDUS = "individus", _("تبرعات الأفراد")
        COOPERATION = "cooperation", _("التعاون الوطني")
        INDH = "indh", _("المبادرة الوطنية للتنمية البشرية")
        ENTREPRISES = "entreprises", _("تبرعات المقاولات")
        AGR = "agr", _("أنشطة مدرة للدخل")

    mois = models.DateField(_("الشهر"))
    source = models.CharField(max_length=20, choices=Source.choices)
    montant = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["mois", "source"], name="unique_recette_mois_source")
        ]
        ordering = ["mois"]

    def __str__(self):
        return f"{self.get_source_display()} - {self.mois:%Y-%m}"
