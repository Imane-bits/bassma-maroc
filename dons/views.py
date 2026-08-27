import csv
import io

from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext as _

from aide.models import DemandeAide
from users.mixins import role_required

from .emails import notifier_donateur_affectation
from .forms import AffectationForm, DonForm
from .impact import donnees_espace_donateur
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
    periode = request.GET.get("periode", "6mois")
    if periode not in ("mois", "6mois", "annee"):
        periode = "6mois"
    contexte = donnees_espace_donateur(request.user, periode)
    return render(request, "dons/mes_dons.html", contexte)


@role_required("donateur")
def exporter_mes_dons(request):
    dons = Don.objects.filter(donateur=request.user).order_by("date_don")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="mes_dons.csv"'
    writer = csv.writer(response)
    writer.writerow(["Date", "Montant (MAD)", "Type", "Statut"])
    for don in dons:
        writer.writerow(
            [don.date_don, don.montant, don.get_type_don_display(), don.get_statut_display()]
        )
    return response


@role_required("donateur")
def recu_fiscal(request):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    annee = timezone.localdate().year
    dons = Don.objects.filter(donateur=request.user, date_don__year=annee).order_by("date_don")
    total = dons.aggregate(t=Sum("montant"))["t"] or 0
    donateur = request.user

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    styles = getSampleStyleSheet()
    nom = donateur.get_full_name() or donateur.username

    elements = [
        Paragraph("Association Bassma Maroc", styles["Title"]),
        Paragraph(f"Reçu de dons — année {annee}", styles["Heading2"]),
        Spacer(1, 12),
        Paragraph(f"Donateur : {nom}", styles["Normal"]),
        Paragraph(f"Email : {donateur.email or '-'}", styles["Normal"]),
        Spacer(1, 16),
    ]

    data = [["Date", "Montant (MAD)", "Type"]]
    for don in dons:
        data.append([str(don.date_don), f"{don.montant:,}", don.get_type_don_display()])
    data.append(["", "", ""])
    data.append(["Total", f"{total:,}", ""])

    table = Table(data, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#14432B")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -2), 0.5, colors.grey),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]
        )
    )
    elements.append(table)
    elements.append(Spacer(1, 20))
    elements.append(
        Paragraph(
            "Ce document récapitule les dons versés à l'association Bassma Maroc "
            f"au cours de l'année {annee}, à titre indicatif.",
            styles["Normal"],
        )
    )

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="recu_dons_{annee}.pdf"'
    return response


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
