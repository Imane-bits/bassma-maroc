from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from aide.models import DemandeAide
from dons.models import Don
from ecole.models import PaiementScolarite, PreinscriptionEleve

from .forms import InscriptionForm
from .mixins import role_required

User = get_user_model()


def register(request):
    if request.method == "POST":
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.is_active:
                login(request, user)
                return redirect("home")
            return redirect("compte_en_attente")
    else:
        form = InscriptionForm()
    return render(request, "registration/inscription.html", {"form": form})


def compte_en_attente(request):
    return render(request, "compte_en_attente.html")


def home(request):
    return render(request, "home.html")


@role_required("responsable")
def espace_responsable(request):
    from django.db.models import Sum

    demandes_en_attente = DemandeAide.objects.filter(
        statut=DemandeAide.Statut.EN_ATTENTE
    ).select_related("beneficiaire")

    stats = {
        "demandes_en_attente": demandes_en_attente.count(),
        "dons_a_affecter": Don.objects.exclude(statut=Don.Statut.DISTRIBUE).count(),
        "total_dons": Don.objects.aggregate(total=Sum("montant"))["total"] or 0,
        "paiements_en_retard": PaiementScolarite.objects.filter(
            statut_paiement=PaiementScolarite.StatutPaiement.EN_RETARD
        ).count(),
        "preinscriptions_en_attente": PreinscriptionEleve.objects.filter(
            statut=PreinscriptionEleve.Statut.EN_ATTENTE
        ).count(),
        "comptes_en_attente": User.objects.filter(
            role=User.Role.RESPONSABLE, is_active=False
        ).count(),
    }
    return render(
        request,
        "espace_responsable.html",
        {
            "stats": stats,
            "dernieres_demandes": demandes_en_attente.order_by("-date_soumission")[:5],
        },
    )


@role_required("responsable")
def comptes_en_attente(request):
    comptes = User.objects.filter(
        role=User.Role.RESPONSABLE, is_active=False
    ).order_by("date_joined")
    return render(request, "comptes_en_attente.html", {"comptes": comptes})


@role_required("responsable")
def activer_compte(request, pk):
    compte = get_object_or_404(
        User, pk=pk, role=User.Role.RESPONSABLE, is_active=False
    )
    if request.method == "POST":
        compte.is_active = True
        compte.save(update_fields=["is_active"])
        messages.success(request, _("تم تفعيل الحساب."))
    return redirect("comptes_en_attente")
