from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from aide.models import DemandeAide
from users.mixins import role_required

from .emails import notifier_donateur_affectation
from .forms import AffectationForm, DonForm
from .models import Affectation, Don


@role_required("donateur")
def creer_don(request):
    if request.method == "POST":
        form = DonForm(request.POST)
        demande_pk = request.POST.get("demande_aide")
        if form.is_valid():
            don = form.save(commit=False)
            don.donateur = request.user
            don.save()
            messages.success(request, _("شكرًا على تبرّعك."))
            return redirect("dons:mes_dons")
    else:
        demande_pk = request.GET.get("demande")
        form = DonForm(initial={"demande_aide": demande_pk} if demande_pk else {})
    cible_demande = DemandeAide.objects.filter(pk=demande_pk).first() if demande_pk else None
    return render(
        request, "dons/creer_don.html", {"form": form, "cible_demande": cible_demande}
    )


@role_required("donateur")
def mes_dons(request):
    dons = (
        Don.objects.filter(donateur=request.user)
        .prefetch_related("affectations")
        .order_by("-date_don")
    )
    return render(request, "dons/mes_dons.html", {"dons": dons})


@role_required("responsable")
def liste_dons_a_affecter(request):
    dons = (
        Don.objects.exclude(statut=Don.Statut.DISTRIBUE)
        .annotate(total_affecte=Sum("affectations__montant_affecte"))
        .order_by("-date_don")
    )
    return render(request, "dons/liste_dons.html", {"dons": dons})


@role_required("responsable")
def don_detail(request, pk):
    don = get_object_or_404(Don.objects.select_related("donateur", "demande_aide"), pk=pk)
    affectations = don.affectations.select_related(
        "budget", "demande_aide", "demande_aide__beneficiaire", "validee_par"
    ).order_by("-date_affectation")
    total_affecte = affectations.aggregate(total=Sum("montant_affecte"))["total"] or 0
    return render(
        request,
        "dons/don_detail.html",
        {
            "don": don,
            "affectations": affectations,
            "total_affecte": total_affecte,
            "reste": don.montant - total_affecte,
        },
    )


@role_required("responsable")
def creer_affectation(request):
    if request.method == "POST":
        form = AffectationForm(request.POST)
        if form.is_valid():
            affectation = form.save(commit=False)
            affectation.validee_par = request.user
            affectation.save()

            don = affectation.don
            total = don.affectations.aggregate(total=Sum("montant_affecte"))["total"] or 0
            don.statut = (
                Don.Statut.DISTRIBUE if total >= don.montant else Don.Statut.EN_AFFECTATION
            )
            don.save(update_fields=["statut"])

            notifier_donateur_affectation(affectation)
            messages.success(request, _("تم إنشاء التوزيع، وتم إشعار المتبرّع."))
            return redirect("dons:liste_dons")
    else:
        form = AffectationForm()
    return render(request, "dons/creer_affectation.html", {"form": form})
