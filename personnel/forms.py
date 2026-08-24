from django import forms

from .models import Membre


class MembreForm(forms.ModelForm):
    class Meta:
        model = Membre
        fields = ["nom", "prenom", "poste", "telephone", "email", "date_entree"]
        widgets = {"date_entree": forms.DateInput(attrs={"type": "date"})}
