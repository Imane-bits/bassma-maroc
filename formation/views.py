from django.shortcuts import render


def bientot_disponible(request):
    return render(request, "bientot_disponible.html")
