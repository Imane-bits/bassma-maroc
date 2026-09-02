from datetime import date

from django.db.models import F

from .models import Budget, DepenseMensuelle, RecetteMensuelle

CIBLE_A_PROGRAMME = {
    "beneficiaire": DepenseMensuelle.Programme.AIDE,
    "ecole": DepenseMensuelle.Programme.ECOLE,
    "centre_formation": DepenseMensuelle.Programme.FORMATION,
}


def enregistrer_recette_don(don):
    mois = date(don.date_don.year, don.date_don.month, 1)
    recette, _created = RecetteMensuelle.objects.get_or_create(
        mois=mois, source=RecetteMensuelle.Source.INDIVIDUS, defaults={"montant": 0}
    )
    RecetteMensuelle.objects.filter(pk=recette.pk).update(montant=F("montant") + don.montant)


def enregistrer_depense_affectation(affectation):
    programme = CIBLE_A_PROGRAMME.get(affectation.cible)
    if programme:
        mois = date(affectation.date_affectation.year, affectation.date_affectation.month, 1)
        depense, _created = DepenseMensuelle.objects.get_or_create(
            mois=mois, programme=programme, defaults={"montant": 0}
        )
        DepenseMensuelle.objects.filter(pk=depense.pk).update(
            montant=F("montant") + affectation.montant_affecte
        )

    Budget.objects.filter(pk=affectation.budget_id).update(
        depenses=F("depenses") + affectation.montant_affecte
    )
