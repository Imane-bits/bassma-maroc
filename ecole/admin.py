from django.contrib import admin
from .models import Enseignant, Eleve, PaiementScolarite, PreinscriptionEleve

admin.site.register(Enseignant)
admin.site.register(Eleve)
admin.site.register(PaiementScolarite)
admin.site.register(PreinscriptionEleve)
