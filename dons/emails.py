from django.conf import settings
from django.core.mail import send_mail


def notifier_donateur_affectation(affectation):
    don = affectation.don
    destinataire = don.donateur.email
    if not destinataire:
        return

    sujet = "Votre don a été affecté"
    corps_lignes = [
        f"Bonjour {don.donateur.first_name},",
        "",
        f"Votre don de {don.montant} MAD a été affecté :",
        f"- Montant affecté : {affectation.montant_affecte} MAD",
        f"- Destination : {affectation.get_cible_display()}",
    ]
    if affectation.demande_aide_id:
        corps_lignes.append(f"- Demande concernée : #{affectation.demande_aide_id}")

    send_mail(
        sujet,
        "\n".join(corps_lignes),
        getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@bassmamaroc.local"),
        [destinataire],
        fail_silently=False,
    )
