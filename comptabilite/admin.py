from django.contrib import admin

from .models import Budget, DepenseMensuelle, RecetteMensuelle


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ("module", "periode", "recettes", "depenses", "solde")
    list_filter = ("module",)
    search_fields = ("periode",)


@admin.register(DepenseMensuelle)
class DepenseMensuelleAdmin(admin.ModelAdmin):
    list_display = ("mois", "programme", "montant")
    list_filter = ("programme",)


@admin.register(RecetteMensuelle)
class RecetteMensuelleAdmin(admin.ModelAdmin):
    list_display = ("mois", "source", "montant")
    list_filter = ("source",)
