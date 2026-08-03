from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import InscriptionForm
from .mixins import role_required


def register(request):
    if request.method == "POST":
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = InscriptionForm()
    return render(request, "registration/inscription.html", {"form": form})


@login_required
def home(request):
    return render(request, "home.html")


@role_required("responsable")
def espace_responsable(request):
    return render(request, "espace_responsable.html")
