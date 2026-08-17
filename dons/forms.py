from django import forms
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _

from aide.models import DemandeAide

from .models import Affectation, Don


class DonForm(forms.ModelForm):
    type_don = forms.ChoiceField(choices=Don.TypeDon.choices, widget=forms.RadioSelect)

    class Meta:
        model = Don
        fields = ["montant", "type_don", "demande_aide"]
        widgets = {"demande_aide": forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["demande_aide"].queryset = DemandeAide.objects.exclude(
            statut=DemandeAide.Statut.REFUSEE
        )
        self.fields["demande_aide"].required = False


class AffectationForm(forms.ModelForm):
    cible = forms.ChoiceField(choices=Affectation.Cible.choices)

    class Meta:
        model = Affectation
        fields = ["don", "budget", "montant_affecte", "cible", "demande_aide"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["don"].queryset = Don.objects.exclude(statut=Don.Statut.DISTRIBUE)
        self.fields["demande_aide"].queryset = DemandeAide.objects.exclude(
            statut=DemandeAide.Statut.REFUSEE
        )
        self.fields["demande_aide"].required = False

    def clean(self):
        cleaned_data = super().clean()
        cible = cleaned_data.get("cible")
        demande_aide = cleaned_data.get("demande_aide")
        if cible == Affectation.Cible.BENEFICIAIRE and not demande_aide:
            self.add_error("demande_aide", _("مطلوب عند اختيار وجهة «مستفيد»."))
        if cible and cible != Affectation.Cible.BENEFICIAIRE and demande_aide:
            self.add_error("demande_aide", _("لا يجب تحديده لهذه الوجهة."))

        don = cleaned_data.get("don")
        montant_affecte = cleaned_data.get("montant_affecte")
        if don and montant_affecte:
            deja_affecte = don.affectations.aggregate(total=Sum("montant_affecte"))["total"] or 0
            if montant_affecte > (don.montant - deja_affecte):
                self.add_error("montant_affecte", _("يتجاوز الرصيد المتاح لهذا التبرّع."))
        return cleaned_data
