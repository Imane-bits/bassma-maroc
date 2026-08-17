from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from users.mixins import role_required

from .forms import BeneficiaireProfilForm, DemandeAideForm, PiecesJustificativesForm
from .models import Beneficiaire, DemandeAide, PieceJustificative


def soumettre_demande(request):
    if request.method == "POST":
        profil_form = BeneficiaireProfilForm(request.POST)
        demande_form = DemandeAideForm(request.POST)
        pieces_form = PiecesJustificativesForm(request.POST, request.FILES)
        if profil_form.is_valid() and demande_form.is_valid() and pieces_form.is_valid():
            with transaction.atomic():
                profil_data = dict(profil_form.cleaned_data)
                cin = profil_data.pop("cin")
                profil, _created = Beneficiaire.objects.update_or_create(
                    cin=cin, defaults=profil_data
                )
                demande = demande_form.save(commit=False)
                demande.beneficiaire = profil
                demande.full_clean()
                demande.save()
                for fichier in pieces_form.cleaned_data["fichiers"]:
                    PieceJustificative.objects.create(demande=demande, fichier=fichier)
            return redirect("aide:confirmation", numero_dossier=demande.numero_dossier)
    else:
        profil_form = BeneficiaireProfilForm()
        demande_form = DemandeAideForm()
        pieces_form = PiecesJustificativesForm()
    return render(
        request,
        "aide/soumettre_demande.html",
        {
            "profil_form": profil_form,
            "demande_form": demande_form,
            "pieces_form": pieces_form,
        },
    )


def confirmation(request, numero_dossier):
    demande = get_object_or_404(DemandeAide, numero_dossier=numero_dossier)
    return render(request, "aide/confirmation.html", {"demande": demande})


def suivi_dossier(request):
    demande = None
    if request.method == "POST":
        numero_dossier = request.POST.get("numero_dossier", "").strip()
        demande = DemandeAide.objects.filter(numero_dossier=numero_dossier).first()
        if demande is None:
            messages.error(request, _("Aucun dossier trouvé avec ce numéro."))
    return render(request, "aide/suivi_dossier.html", {"demande": demande})


@role_required("responsable")
def demande_detail(request, pk):
    demande = get_object_or_404(DemandeAide, pk=pk)
    return render(request, "aide/demande_detail.html", {"demande": demande})


@role_required("responsable")
def liste_demandes(request):
    statut = request.GET.get("statut", "en_attente")
    demandes = DemandeAide.objects.all()
    if statut:
        demandes = demandes.filter(statut=statut)
    return render(
        request,
        "aide/liste_demandes.html",
        {"demandes": demandes.order_by("-date_soumission"), "statut": statut},
    )


@role_required("responsable")
def accepter_demande(request, pk):
    demande = get_object_or_404(DemandeAide, pk=pk)
    if request.method == "POST":
        demande.statut = DemandeAide.Statut.ACCEPTEE
        demande.save(update_fields=["statut"])
        messages.success(request, _("Demande acceptée."))
    return redirect("aide:liste_demandes")


@role_required("responsable")
def refuser_demande(request, pk):
    demande = get_object_or_404(DemandeAide, pk=pk)
    if request.method == "POST":
        demande.statut = DemandeAide.Statut.REFUSEE
        demande.save(update_fields=["statut"])
        messages.success(request, _("Demande refusée."))
    return redirect("aide:liste_demandes")
