import csv

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render

from users.mixins import role_required

from .models import Budget


@role_required("responsable")
def consolidation(request):
    par_module = list(
        Budget.objects.values("module")
        .annotate(total_recettes=Sum("recettes"), total_depenses=Sum("depenses"))
        .order_by("module")
    )
    labels = dict(Budget.Module.choices)
    for ligne in par_module:
        ligne["module_display"] = labels[ligne["module"]]
        ligne["solde"] = (ligne["total_recettes"] or 0) - (ligne["total_depenses"] or 0)

    total_recettes = sum(ligne["total_recettes"] or 0 for ligne in par_module)
    total_depenses = sum(ligne["total_depenses"] or 0 for ligne in par_module)
    return render(
        request,
        "comptabilite/consolidation.html",
        {
            "par_module": par_module,
            "total_recettes": total_recettes,
            "total_depenses": total_depenses,
            "solde": total_recettes - total_depenses,
        },
    )


@role_required("responsable")
def bilan_financier(request):
    periode = request.GET.get("periode", "")
    budgets = Budget.objects.all().order_by("-periode", "module")
    if periode:
        budgets = budgets.filter(periode=periode)
    periodes = (
        Budget.objects.order_by("-periode").values_list("periode", flat=True).distinct()
    )
    return render(
        request,
        "comptabilite/bilan_financier.html",
        {"budgets": budgets, "periode": periode, "periodes": periodes},
    )


@role_required("responsable")
def exporter_donnees(request):
    periode = request.GET.get("periode", "")
    budgets = Budget.objects.all().order_by("periode", "module")
    if periode:
        budgets = budgets.filter(periode=periode)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="bilan_comptable.csv"'
    writer = csv.writer(response)
    writer.writerow(["Module", "Période", "Recettes", "Dépenses", "Solde"])
    for budget in budgets:
        writer.writerow(
            [
                budget.get_module_display(),
                budget.periode,
                budget.recettes,
                budget.depenses,
                budget.solde,
            ]
        )
    return response
