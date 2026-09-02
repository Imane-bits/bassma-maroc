from django.contrib import admin

from .models import Enseignant, Eleve, PaiementScolarite, PreinscriptionEleve


@admin.register(Enseignant)
class EnseignantAdmin(admin.ModelAdmin):
    list_display = ("user", "matiere_niveau")
    search_fields = ("user__username", "user__email", "matiere_niveau")


@admin.register(Eleve)
class EleveAdmin(admin.ModelAdmin):
    list_display = ("nom", "prenom", "classe", "tuteur_nom", "tuteur_contact")
    list_filter = ("classe",)
    search_fields = ("nom", "prenom", "tuteur_nom", "tuteur_contact")


@admin.register(PaiementScolarite)
class PaiementScolariteAdmin(admin.ModelAdmin):
    list_display = ("eleve", "montant", "date_echeance", "statut_paiement")
    list_filter = ("statut_paiement",)
    search_fields = ("eleve__nom", "eleve__prenom")


@admin.register(PreinscriptionEleve)
class PreinscriptionEleveAdmin(admin.ModelAdmin):
    list_display = (
        "numero_dossier",
        "nom_enfant",
        "prenom_enfant",
        "tuteur_nom",
        "statut",
        "date_soumission",
    )
    list_filter = ("statut",)
    search_fields = ("numero_dossier", "nom_enfant", "prenom_enfant", "tuteur_nom", "tuteur_contact")
