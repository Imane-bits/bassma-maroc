from datetime import date

from django.db.models import Sum
from django.utils import dateformat, timezone
from django.utils.translation import get_language, gettext_lazy as _

from aide.models import Beneficiaire, DemandeAide

from .models import Affectation, Don

PERIODES = {
    "mois": 1,
    "6mois": 6,
    "annee": 12,
}

CATEGORIE_LABELS = {
    "famille": _("كفالة أسرة"),
    "scolaire": _("دعم مدرسي"),
    "sante": _("دعم صحي"),
    "general": _("دعم عام"),
}

CIBLE_LABELS = {
    "beneficiaire": _("مستفيدون"),
    "ecole": _("المدرسة"),
    "centre_formation": _("مركز التكوين"),
}

MOIS_AR_MAROC = {
    1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل", 5: "ماي", 6: "يونيو",
    7: "يوليوز", 8: "غشت", 9: "شتنبر", 10: "أكتوبر", 11: "نونبر", 12: "دجنبر",
}


def mois_label(mois, court=False):
    if get_language() == "ar":
        nom = MOIS_AR_MAROC[mois.month]
        return f"{nom} {mois.year % 100 if court else mois.year}"
    return dateformat.format(mois, "M y" if court else "F Y")


def _derniers_mois(n):
    today = timezone.localdate()
    mois = []
    annee, moisnum = today.year, today.month
    for _i in range(n):
        mois.append(date(annee, moisnum, 1))
        moisnum -= 1
        if moisnum == 0:
            moisnum = 12
            annee -= 1
    return list(reversed(mois))


def categorie_impact(don):
    if don.type_don == Don.TypeDon.MENSUEL:
        return "famille"
    if don.demande_aide_id:
        categorie = don.demande_aide.categorie
        if categorie == DemandeAide.Categorie.ETUDE:
            return "scolaire"
        if categorie == DemandeAide.Categorie.SANTE:
            return "sante"
    return "general"


def beneficiaires_touches(donateur):
    directs = DemandeAide.objects.filter(dons_cibles__donateur=donateur)
    via_affectation = DemandeAide.objects.filter(
        affectations__don__donateur=donateur, affectations__cible="beneficiaire"
    )
    demandes = (directs | via_affectation).distinct()
    return Beneficiaire.objects.filter(demandes_aide__in=demandes).distinct()


def donnees_espace_donateur(donateur, periode):
    n_mois = PERIODES.get(periode, 6)
    mois_liste = _derniers_mois(n_mois)
    depuis = mois_liste[0]
    today = timezone.localdate()

    tous_les_dons = Don.objects.filter(donateur=donateur)
    dons_periode = list(tous_les_dons.filter(date_don__gte=depuis).order_by("-date_don"))

    total_periode = sum(d.montant for d in dons_periode)
    total_all_time = tous_les_dons.aggregate(t=Sum("montant"))["t"] or 0
    nb_contributions = tous_les_dons.count()
    montant_ce_mois = sum(
        d.montant for d in dons_periode
        if d.date_don.year == today.year and d.date_don.month == today.month
    )
    dons_mensuels_actifs = sum(
        1 for d in dons_periode
        if d.type_don == Don.TypeDon.MENSUEL
        and d.date_don.year == today.year and d.date_don.month == today.month
    )

    beneficiaires = beneficiaires_touches(donateur)
    nb_villes = len({b.ville for b in beneficiaires if b.ville})
    nb_familles = beneficiaires.count()

    par_mois = {m: 0 for m in mois_liste}
    dons_par_mois = {m: [] for m in mois_liste}
    for don in dons_periode:
        cle = date(don.date_don.year, don.date_don.month, 1)
        if cle in par_mois:
            par_mois[cle] += don.montant
            dons_par_mois[cle].append(don)

    affectations_par_don = {}
    toutes_affectations = Affectation.objects.filter(
        don_id__in=[d.pk for d in dons_periode]
    ).only("don_id", "cible", "montant_affecte")
    for affectation in toutes_affectations:
        affectations_par_don.setdefault(affectation.don_id, []).append(affectation)

    graphique = []
    for m in mois_liste:
        montant = par_mois[m]
        par_cible = {}
        for don in dons_par_mois[m]:
            for affectation in affectations_par_don.get(don.pk, []):
                par_cible[affectation.cible] = (
                    par_cible.get(affectation.cible, 0) + affectation.montant_affecte
                )
        total_affecte = sum(par_cible.values())
        allocs = [
            {"label": CIBLE_LABELS[cible], "montant": mnt}
            for cible, mnt in sorted(par_cible.items(), key=lambda kv: -kv[1])
        ]
        graphique.append(
            {
                "mois": m,
                "mois_label": mois_label(m, court=True),
                "montant": montant,
                "allocs": allocs,
                "non_affecte": montant - total_affecte,
            }
        )
    max_mois = max((ligne["montant"] for ligne in graphique), default=0)
    for ligne in graphique:
        ligne["hauteur_pct"] = round((ligne["montant"] / max_mois) * 100) if max_mois else 0

    repartition = {}
    for don in dons_periode:
        cle = categorie_impact(don)
        repartition[cle] = repartition.get(cle, 0) + don.montant
    repartition_lignes = [
        {
            "label": CATEGORIE_LABELS[cle],
            "montant": montant,
            "pourcentage": round((montant / total_periode) * 100) if total_periode else 0,
        }
        for cle, montant in sorted(repartition.items(), key=lambda kv: -kv[1])
    ]

    detail_mensuel = [
        {
            "mois": m,
            "mois_label": mois_label(m),
            "dons": dons_par_mois[m],
            "total": par_mois[m],
        }
        for m in reversed(mois_liste)
        if dons_par_mois[m]
    ]

    log = [
        {"don": don, "categorie_label": CATEGORIE_LABELS[categorie_impact(don)]}
        for don in dons_periode
    ]

    return {
        "periode": periode,
        "nb_villes": nb_villes,
        "nb_familles": nb_familles,
        "total_periode": total_periode,
        "total_all_time": total_all_time,
        "nb_contributions": nb_contributions,
        "dons_mensuels_actifs": dons_mensuels_actifs,
        "montant_ce_mois": montant_ce_mois,
        "graphique": graphique,
        "repartition": repartition_lignes,
        "detail_mensuel": detail_mensuel,
        "log": log,
    }
