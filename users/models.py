from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Role(models.TextChoices):
        DONATEUR = "donateur", _("Donateur")
        ENSEIGNANT = "enseignant", _("Enseignant")
        RESPONSABLE = "responsable", _("Responsable")

    role = models.CharField(_("rôle"), max_length=20, choices=Role.choices)
