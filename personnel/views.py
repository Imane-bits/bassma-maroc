from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from users.mixins import role_required

from .forms import MembreForm
from .models import Membre


@role_required("responsable")
def liste_membres(request):
    statut = request.GET.get("statut", "actif")
    membres = Membre.objects.all()
    if statut:
        membres = membres.filter(statut=statut)
    page_obj = Paginator(membres.order_by("nom"), 20).get_page(request.GET.get("page"))
    return render(
        request,
        "personnel/liste_membres.html",
        {"membres": page_obj, "page_obj": page_obj, "statut": statut},
    )


@role_required("responsable")
def creer_membre(request):
    if request.method == "POST":
        form = MembreForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("تمت إضافة العضو."))
            return redirect("personnel:liste_membres")
    else:
        form = MembreForm()
    return render(request, "personnel/creer_membre.html", {"form": form})


@role_required("responsable")
def modifier_membre(request, pk):
    membre = get_object_or_404(Membre, pk=pk)
    if request.method == "POST":
        form = MembreForm(request.POST, instance=membre)
        if form.is_valid():
            form.save()
            messages.success(request, _("تم تحديث معطيات العضو."))
            return redirect("personnel:liste_membres")
    else:
        form = MembreForm(instance=membre)
    return render(
        request, "personnel/creer_membre.html", {"form": form, "membre": membre}
    )


@role_required("responsable")
def desactiver_membre(request, pk):
    membre = get_object_or_404(Membre, pk=pk)
    if request.method == "POST":
        membre.statut = Membre.Statut.INACTIF
        membre.save(update_fields=["statut"])
        messages.success(request, _("تم إلغاء تفعيل العضو."))
    return redirect("personnel:liste_membres")


@role_required("responsable")
def activer_membre(request, pk):
    membre = get_object_or_404(Membre, pk=pk)
    if request.method == "POST":
        membre.statut = Membre.Statut.ACTIF
        membre.save(update_fields=["statut"])
        messages.success(request, _("تم إعادة تفعيل العضو."))
    return redirect("personnel:liste_membres")
