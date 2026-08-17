from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Beneficiaire, DemandeAide


class BeneficiaireProfilForm(forms.ModelForm):
    class Meta:
        model = Beneficiaire
        fields = [
            "nom",
            "prenom",
            "cin",
            "date_naissance",
            "telephone",
            "ville",
            "adresse",
            "situation_familiale",
            "nombre_enfants",
            "enfants_scolarises",
            "probleme_sante",
        ]
        widgets = {"date_naissance": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cin"].required = True


class DemandeAideForm(forms.ModelForm):
    consentement_donnees = forms.BooleanField(
        required=True,
        label=_("J'accepte le traitement de mes données personnelles (loi 09-08)"),
    )

    class Meta:
        model = DemandeAide
        fields = ["description", "urgence", "type_aide", "consentement_donnees"]


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]
        return single_file_clean(data, initial)


class PiecesJustificativesForm(forms.Form):
    fichiers = MultipleFileField(required=False, label=_("Pièces justificatives"))
