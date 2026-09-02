from django.conf import settings
from django.core.mail import send_mail


def notifier_beneficiaire_demande(demande, acceptee):
    beneficiaire = demande.beneficiaire
    destinataire = beneficiaire.email
    if not destinataire:
        return

    if acceptee:
        sujet = "تم قبول طلبكم"
        corps_lignes = [
            f"مرحبًا {beneficiaire.prenom}،",
            "",
            f"تم قبول طلبكم رقم {demande.numero_dossier} ({demande.titre}).",
        ]
    else:
        sujet = "بخصوص طلبكم"
        corps_lignes = [
            f"مرحبًا {beneficiaire.prenom}،",
            "",
            f"للأسف، لم يتم قبول طلبكم رقم {demande.numero_dossier} ({demande.titre}).",
        ]

    send_mail(
        sujet,
        "\n".join(corps_lignes),
        getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@bassmamaroc.local"),
        [destinataire],
        fail_silently=False,
    )
