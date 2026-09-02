from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext as _

from users.mixins import role_required
from users.ratelimit import is_rate_limited

from .forms import PreinscriptionEleveForm
from .models import PaiementScolarite, PreinscriptionEleve


def preinscrire(request):
    if request.method == "POST":
        if request.POST.get("site_web"):
            return redirect("ecole:preinscrire")
        if is_rate_limited(request, "preinscrire"):
            messages.error(request, _("عدد كبير جدًا من المحاولات. حاول مرة أخرى لاحقًا."))
            return redirect("ecole:preinscrire")
        form = PreinscriptionEleveForm(request.POST)
        if form.is_valid():
            preinscription = form.save()
            return redirect(
                "ecole:confirmation", numero_dossier=preinscription.numero_dossier
            )
    else:
        form = PreinscriptionEleveForm()
    return render(request, "ecole/preinscrire.html", {"form": form})


def confirmation(request, numero_dossier):
    preinscription = get_object_or_404(
        PreinscriptionEleve, numero_dossier=numero_dossier
    )
    return render(request, "ecole/confirmation.html", {"preinscription": preinscription})


def suivi_preinscription(request):
    preinscription = None
    if request.method == "POST":
        if is_rate_limited(request, "suivi_preinscription", limit=20, window_seconds=600):
            messages.error(request, _("عدد كبير جدًا من المحاولات. حاول مرة أخرى لاحقًا."))
            return render(
                request, "ecole/suivi_preinscription.html", {"preinscription": None}
            )
        numero_dossier = request.POST.get("numero_dossier", "").strip()
        preinscription = PreinscriptionEleve.objects.filter(
            numero_dossier=numero_dossier
        ).first()
        if preinscription is None:
            messages.error(request, _("لم يتم العثور على ملف بهذا الرقم."))
    return render(
        request, "ecole/suivi_preinscription.html", {"preinscription": preinscription}
    )


@role_required("responsable")
def liste_preinscriptions(request):
    statut = request.GET.get("statut", "en_attente")
    preinscriptions = PreinscriptionEleve.objects.all()
    if statut:
        preinscriptions = preinscriptions.filter(statut=statut)
    page_obj = Paginator(preinscriptions.order_by("-date_soumission"), 20).get_page(
        request.GET.get("page")
    )
    return render(
        request,
        "ecole/liste_preinscriptions.html",
        {"preinscriptions": page_obj, "page_obj": page_obj, "statut": statut},
    )


@role_required("responsable")
def accepter_preinscription(request, pk):
    preinscription = get_object_or_404(PreinscriptionEleve, pk=pk)
    if request.method == "POST":
        preinscription.statut = PreinscriptionEleve.Statut.ACCEPTEE
        preinscription.save(update_fields=["statut"])
        messages.success(
            request,
            _("تم قبول الطلب. يرجى إنشاء ملف التلميذ من واجهة الإدارة."),
        )
    return redirect("ecole:liste_preinscriptions")


@role_required("responsable")
def refuser_preinscription(request, pk):
    preinscription = get_object_or_404(PreinscriptionEleve, pk=pk)
    if request.method == "POST":
        preinscription.statut = PreinscriptionEleve.Statut.REFUSEE
        preinscription.save(update_fields=["statut"])
        messages.success(request, _("تم رفض الطلب."))
    return redirect("ecole:liste_preinscriptions")


@role_required("responsable")
def liste_paiements(request):
    PaiementScolarite.objects.filter(
        statut_paiement=PaiementScolarite.StatutPaiement.DU,
        date_echeance__lt=timezone.localdate(),
    ).update(statut_paiement=PaiementScolarite.StatutPaiement.EN_RETARD)

    statut = request.GET.get("statut", "")
    paiements = PaiementScolarite.objects.select_related("eleve").order_by("date_echeance")
    if statut:
        paiements = paiements.filter(statut_paiement=statut)
    page_obj = Paginator(paiements, 20).get_page(request.GET.get("page"))
    return render(
        request,
        "ecole/liste_paiements.html",
        {"paiements": page_obj, "page_obj": page_obj, "statut": statut},
    )


@role_required("responsable")
def marquer_paye(request, pk):
    paiement = get_object_or_404(PaiementScolarite, pk=pk)
    if request.method == "POST":
        paiement.statut_paiement = PaiementScolarite.StatutPaiement.PAYE
        paiement.save(update_fields=["statut_paiement"])
        messages.success(request, _("تم تسجيل الدفعة كمدفوعة."))
    return redirect("ecole:liste_paiements")
