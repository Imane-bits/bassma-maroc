from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Beneficiaire, DemandeAide


class BeneficiaireProfilForm(forms.ModelForm):
    nom_complet = forms.CharField(label=_("الاسم الكامل"))

    class Meta:
        model = Beneficiaire
        fields = [
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
        self.order_fields(
            ["nom_complet", "cin", "date_naissance", "telephone", "ville", "adresse"]
        )

    def clean_nom_complet(self):
        nom_complet = self.cleaned_data["nom_complet"].strip()
        if not nom_complet:
            raise forms.ValidationError(_("هذا الحقل مطلوب."))
        return nom_complet

    def save(self, commit=True):
        instance = super().save(commit=False)
        nom_complet = self.cleaned_data["nom_complet"]
        prenom, _sep, nom = nom_complet.partition(" ")
        instance.prenom = prenom
        instance.nom = nom or prenom
        if commit:
            instance.save()
        return instance


class DemandeAideForm(forms.ModelForm):
    categorie = forms.ChoiceField(
        choices=DemandeAide.Categorie.choices, widget=forms.RadioSelect
    )
    urgence = forms.ChoiceField(
        choices=DemandeAide.Urgence.choices, widget=forms.RadioSelect
    )
    consentement_donnees = forms.BooleanField(
        required=True,
        label=_("أوافق على معالجة معطياتي الشخصية طبقاً للقانون رقم 09.08"),
    )

    class Meta:
        model = DemandeAide
        fields = [
            "titre",
            "categorie",
            "urgence",
            "description",
            "montant_demande",
            "consentement_donnees",
        ]


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
