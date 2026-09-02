from django.conf import settings
from django.core.mail import send_mail


def notifier_donateur_affectation(affectation):
    don = affectation.don
    destinataire = don.email_affichage
    if not destinataire:
        return

    sujet = "تم توزيع تبرّعك"
    corps_lignes = [
        f"مرحبًا {don.nom_affichage}،",
        "",
        f"تم توزيع تبرّعك البالغ {don.montant} MAD:",
        f"- المبلغ الموزّع: {affectation.montant_affecte} MAD",
        f"- الوجهة: {affectation.get_cible_display()}",
    ]
    if affectation.demande_aide_id:
        corps_lignes.append(f"- الطلب المعني: #{affectation.demande_aide_id}")

    send_mail(
        sujet,
        "\n".join(corps_lignes),
        getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@bassmamaroc.local"),
        [destinataire],
        fail_silently=False,
    )
