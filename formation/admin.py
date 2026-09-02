from django.contrib import admin

from .models import FormationCouture, InscriptionFormation, Presence, Certification


@admin.register(FormationCouture)
class FormationCoutureAdmin(admin.ModelAdmin):
    list_display = ("intitule", "duree_semaines")
    search_fields = ("intitule",)


@admin.register(InscriptionFormation)
class InscriptionFormationAdmin(admin.ModelAdmin):
    list_display = (
        "numero_inscription",
        "beneficiaire",
        "formation",
        "progression",
        "statut",
        "date_inscription",
    )
    list_filter = ("statut", "formation")
    search_fields = ("numero_inscription", "beneficiaire__nom", "beneficiaire__prenom")


@admin.register(Presence)
class PresenceAdmin(admin.ModelAdmin):
    list_display = ("inscription", "date", "present")
    list_filter = ("present", "date")


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ("numero", "inscription", "date_delivrance")
    search_fields = ("numero",)
