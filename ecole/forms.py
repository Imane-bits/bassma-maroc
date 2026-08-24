from django import forms

from .models import PreinscriptionEleve


class PreinscriptionEleveForm(forms.ModelForm):
    class Meta:
        model = PreinscriptionEleve
        fields = [
            "nom_enfant",
            "prenom_enfant",
            "date_naissance",
            "tuteur_nom",
            "tuteur_contact",
            "adresse",
        ]
        widgets = {"date_naissance": forms.DateInput(attrs={"type": "date"})}
