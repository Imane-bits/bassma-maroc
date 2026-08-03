from django.db import models


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

    def __str__(self):
        return f"Budget {self.module} - {self.periode}"
