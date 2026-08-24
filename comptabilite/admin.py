from django.contrib import admin
from .models import Budget, DepenseMensuelle, RecetteMensuelle

admin.site.register(Budget)
admin.site.register(DepenseMensuelle)
admin.site.register(RecetteMensuelle)
