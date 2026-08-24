from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Budget, DepenseMensuelle, RecetteMensuelle

User = get_user_model()


class BudgetSoldeTests(TestCase):
    def test_solde_est_recettes_moins_depenses(self):
        budget = Budget.objects.create(
            module=Budget.Module.ECOLE, periode="2026-T1", recettes=1000, depenses=400
        )
        self.assertEqual(budget.solde, 600)


class ConsolidationViewTests(TestCase):
    def setUp(self):
        self.responsable = User.objects.create_user(
            username="resp", password="pass1234", role=User.Role.RESPONSABLE
        )
        DepenseMensuelle.objects.create(
            mois=date(2026, 3, 1), programme=DepenseMensuelle.Programme.ECOLE, montant=400
        )
        DepenseMensuelle.objects.create(
            mois=date(2026, 4, 1), programme=DepenseMensuelle.Programme.AIDE, montant=100
        )
        RecetteMensuelle.objects.create(
            mois=date(2026, 3, 1), source=RecetteMensuelle.Source.INDIVIDUS, montant=1000
        )
        RecetteMensuelle.objects.create(
            mois=date(2026, 4, 1), source=RecetteMensuelle.Source.INDH, montant=500
        )

    def test_totaux_consolides(self):
        self.client.force_login(self.responsable)
        response = self.client.get(reverse("comptabilite:consolidation"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_recettes"], 1500)
        self.assertEqual(response.context["total_depenses"], 500)
        self.assertEqual(response.context["resultat"], 1000)

    def test_repartition_par_programme_avec_pourcentages(self):
        self.client.force_login(self.responsable)
        response = self.client.get(reverse("comptabilite:consolidation"))
        depenses = {
            ligne["programme"]: ligne for ligne in response.context["depenses_par_programme"]
        }
        self.assertEqual(depenses["ecole"]["montant"], 400)
        self.assertEqual(depenses["ecole"]["pourcentage"], 80)
        self.assertEqual(depenses["aide"]["montant"], 100)
        self.assertEqual(depenses["aide"]["pourcentage"], 20)

    def test_table_mensuelle_a_une_ligne_par_mois(self):
        self.client.force_login(self.responsable)
        response = self.client.get(reverse("comptabilite:consolidation"))
        table = response.context["table_mensuelle"]
        self.assertEqual(len(table), 2)
        self.assertEqual(table[0]["mois"], date(2026, 3, 1))
        self.assertEqual(table[0]["total"], 400)

    def test_acces_refuse_hors_responsable(self):
        donateur = User.objects.create_user(
            username="don", password="pass1234", role=User.Role.DONATEUR
        )
        self.client.force_login(donateur)
        response = self.client.get(reverse("comptabilite:consolidation"))
        self.assertEqual(response.status_code, 403)


class ExportTests(TestCase):
    def setUp(self):
        self.responsable = User.objects.create_user(
            username="resp2", password="pass1234", role=User.Role.RESPONSABLE
        )
        DepenseMensuelle.objects.create(
            mois=date(2026, 3, 1), programme=DepenseMensuelle.Programme.ECOLE, montant=400
        )
        RecetteMensuelle.objects.create(
            mois=date(2026, 3, 1), source=RecetteMensuelle.Source.INDIVIDUS, montant=1000
        )

    def test_export_excel(self):
        self.client.force_login(self.responsable)
        response = self.client.get(reverse("comptabilite:exporter_excel"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def test_export_pdf(self):
        self.client.force_login(self.responsable)
        response = self.client.get(reverse("comptabilite:exporter_pdf"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
