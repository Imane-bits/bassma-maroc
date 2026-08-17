from django.contrib import admin

from .models import Affectation, Don


@admin.register(Don)
class DonAdmin(admin.ModelAdmin):
    list_display = ("id", "donateur", "montant", "type_don", "statut", "date_don")
    list_filter = ("statut", "type_don")


@admin.register(Affectation)
class AffectationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "don",
        "budget",
        "montant_affecte",
        "cible",
        "demande_aide",
        "validee_par",
        "date_affectation",
    )
    list_filter = ("cible",)
