from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

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
    return render(request, "espace_responsable.html")


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
