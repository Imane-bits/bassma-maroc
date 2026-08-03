from django.contrib import admin
from .models import Enseignant, Eleve, PaiementScolarite

admin.site.register(Enseignant)
admin.site.register(Eleve)
admin.site.register(PaiementScolarite)
