from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext as _

from users.mixins import role_required

from .models import PaiementScolarite


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
    return render(
        request,
        "ecole/liste_paiements.html",
        {"paiements": paiements, "statut": statut},
    )


@role_required("responsable")
def marquer_paye(request, pk):
    paiement = get_object_or_404(PaiementScolarite, pk=pk)
    if request.method == "POST":
        paiement.statut_paiement = PaiementScolarite.StatutPaiement.PAYE
        paiement.save(update_fields=["statut_paiement"])
        messages.success(request, _("Paiement marqué comme payé."))
    return redirect("ecole:liste_paiements")
