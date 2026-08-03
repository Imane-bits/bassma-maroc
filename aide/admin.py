from django.contrib import admin
from .models import Beneficiaire, DemandeAide, PieceJustificative

admin.site.register(Beneficiaire)
admin.site.register(DemandeAide)
admin.site.register(PieceJustificative)
