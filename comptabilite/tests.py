from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Budget

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
        Budget.objects.create(
            module=Budget.Module.ECOLE, periode="2026-T1", recettes=1000, depenses=400
        )
        Budget.objects.create(
            module=Budget.Module.DONS, periode="2026-T1", recettes=500, depenses=100
        )

    def test_totaux_consolides_sur_tous_les_modules(self):
        self.client.force_login(self.responsable)
        response = self.client.get(reverse("comptabilite:consolidation"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_recettes"], 1500)
        self.assertEqual(response.context["total_depenses"], 500)
        self.assertEqual(response.context["solde"], 1000)

    def test_acces_refuse_hors_responsable(self):
        donateur = User.objects.create_user(
            username="don", password="pass1234", role=User.Role.DONATEUR
        )
        self.client.force_login(donateur)
        response = self.client.get(reverse("comptabilite:consolidation"))
        self.assertEqual(response.status_code, 403)
