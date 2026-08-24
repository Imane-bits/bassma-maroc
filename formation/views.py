from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from aide.forms import BeneficiaireProfilForm
from aide.models import Beneficiaire

from .forms import InscriptionFormationForm
from .models import FormationCouture, InscriptionFormation


def liste_formations(request):
    formations = FormationCouture.objects.all()
    return render(request, "formation/liste_formations.html", {"formations": formations})


def inscription_formation(request):
    if request.method == "POST":
        cin = request.POST.get("cin", "").strip()
        profil_instance = Beneficiaire.objects.filter(cin=cin).first() if cin else None
        profil_form = BeneficiaireProfilForm(request.POST, instance=profil_instance)
        inscription_form = InscriptionFormationForm(request.POST)
        if profil_form.is_valid() and inscription_form.is_valid():
            with transaction.atomic():
                profil = profil_form.save()
                inscription = inscription_form.save(commit=False)
                inscription.beneficiaire = profil
                inscription.full_clean()
                inscription.save()
            return redirect(
                "formation:confirmation", numero_inscription=inscription.numero_inscription
            )
    else:
        initial = {}
        formation_id = request.GET.get("formation")
        if formation_id:
            initial["formation"] = formation_id
        profil_form = BeneficiaireProfilForm()
        inscription_form = InscriptionFormationForm(initial=initial)
    return render(
        request,
        "formation/inscription_formation.html",
        {"profil_form": profil_form, "inscription_form": inscription_form},
    )


def confirmation(request, numero_inscription):
    inscription = get_object_or_404(
        InscriptionFormation, numero_inscription=numero_inscription
    )
    return render(request, "formation/confirmation.html", {"inscription": inscription})


def suivi_formation(request):
    inscription = None
    if request.method == "POST":
        numero_inscription = request.POST.get("numero_inscription", "").strip()
        inscription = InscriptionFormation.objects.filter(
            numero_inscription=numero_inscription
        ).first()
        if inscription is None:
            messages.error(request, _("لم يتم العثور على تسجيل بهذا الرقم."))
    return render(request, "formation/suivi_formation.html", {"inscription": inscription})
