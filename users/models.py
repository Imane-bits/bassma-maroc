from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        DONATEUR = "donateur", "Donateur"
        BENEFICIAIRE = "beneficiaire", "Bénéficiaire"
        ENSEIGNANT = "enseignant", "Enseignant"
        RESPONSABLE = "responsable", "Responsable"

    role = models.CharField(max_length=20, choices=Role.choices)
