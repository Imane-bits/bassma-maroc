from django.contrib import admin

from .models import Beneficiaire, DemandeAide, PieceJustificative


class PieceJustificativeInline(admin.TabularInline):
    model = PieceJustificative
    extra = 0


@admin.register(Beneficiaire)
class BeneficiaireAdmin(admin.ModelAdmin):
    list_display = ("nom", "prenom", "cin", "ville", "situation_familiale", "nombre_enfants")
    search_fields = ("nom", "prenom", "cin")


@admin.register(DemandeAide)
class DemandeAideAdmin(admin.ModelAdmin):
    list_display = (
        "numero_dossier",
        "beneficiaire",
        "titre",
        "categorie",
        "urgence",
        "statut",
        "date_soumission",
    )
    list_filter = ("statut", "urgence", "categorie")
    search_fields = (
        "numero_dossier",
        "beneficiaire__cin",
        "beneficiaire__nom",
        "beneficiaire__prenom",
        "description",
    )
    inlines = [PieceJustificativeInline]


admin.site.register(PieceJustificative)
