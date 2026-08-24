from django.db import models
from django.utils.translation import gettext_lazy as _


class Membre(models.Model):
    class Statut(models.TextChoices):
        ACTIF = "actif", _("نشط")
        INACTIF = "inactif", _("غير نشط")

    nom = models.CharField(_("الاسم العائلي"), max_length=100)
    prenom = models.CharField(_("الاسم الشخصي"), max_length=100)
    poste = models.CharField(_("المنصب"), max_length=100)
    telephone = models.CharField(_("الهاتف"), max_length=20, blank=True)
    email = models.EmailField(_("البريد الإلكتروني"), blank=True)
    date_entree = models.DateField(_("تاريخ الالتحاق"), null=True, blank=True)
    statut = models.CharField(
        max_length=10, choices=Statut.choices, default=Statut.ACTIF
    )

    def __str__(self):
        return f"{self.prenom} {self.nom}"
