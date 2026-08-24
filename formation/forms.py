from django import forms
from django.utils.translation import gettext_lazy as _

from .models import InscriptionFormation


class InscriptionFormationForm(forms.ModelForm):
    class Meta:
        model = InscriptionFormation
        fields = ["formation"]
        labels = {"formation": _("التكوين المطلوب")}
