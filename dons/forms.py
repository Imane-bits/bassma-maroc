from django import forms
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _

from aide.models import DemandeAide

from .models import Affectation, Don


class DonForm(forms.ModelForm):
    class Meta:
        model = Don
        fields = ["montant", "type_don"]


class AffectationForm(forms.ModelForm):
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
            self.add_error("demande_aide", _("Requis lorsque la cible est un bénéficiaire."))
        if cible and cible != Affectation.Cible.BENEFICIAIRE and demande_aide:
            self.add_error("demande_aide", _("Ne doit pas être renseigné pour cette cible."))

        don = cleaned_data.get("don")
        montant_affecte = cleaned_data.get("montant_affecte")
        if don and montant_affecte:
            deja_affecte = don.affectations.aggregate(total=Sum("montant_affecte"))["total"] or 0
            if montant_affecte > (don.montant - deja_affecte):
                self.add_error("montant_affecte", _("Dépasse le solde disponible de ce don."))
        return cleaned_data
