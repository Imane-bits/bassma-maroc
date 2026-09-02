from django.contrib import admin

from .models import Membre


@admin.register(Membre)
class MembreAdmin(admin.ModelAdmin):
    list_display = ("nom", "prenom", "poste", "telephone", "statut", "date_entree")
    list_filter = ("statut",)
    search_fields = ("nom", "prenom", "poste", "email")
