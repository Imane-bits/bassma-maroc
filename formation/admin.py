from django.contrib import admin
from .models import FormationCouture, InscriptionFormation, Presence, Certification

admin.site.register(FormationCouture)
admin.site.register(InscriptionFormation)
admin.site.register(Presence)
admin.site.register(Certification)
