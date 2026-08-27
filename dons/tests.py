from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from aide.models import Beneficiaire, DemandeAide
from comptabilite.models import Budget

from .impact import beneficiaires_touches, categorie_impact, donnees_espace_donateur
from .models import Affectation, Don

User = get_user_model()


class CreerDonViewTests(TestCase):
    def setUp(self):
        self.donateur = User.objects.create_user(
            username="don1", password="pass1234", role=User.Role.DONATEUR
        )

    def test_creation_don_associe_le_donateur_connecte(self):
        self.client.force_login(self.donateur)
        response = self.client.post(
            reverse("dons:creer_don"),
            {"montant": "150.00", "type_don": Don.TypeDon.UNIQUE},
        )
        self.assertRedirects(response, reverse("dons:mes_dons"))
        don = Don.objects.get()
        self.assertEqual(don.donateur, self.donateur)
        self.assertEqual(don.montant, Decimal("150.00"))

    def test_acces_refuse_hors_donateur(self):
        responsable = User.objects.create_user(
            username="resp1", password="pass1234", role=User.Role.RESPONSABLE
        )
        self.client.force_login(responsable)
        response = self.client.get(reverse("dons:creer_don"))
        self.assertEqual(response.status_code, 403)


class MesDonsViewTests(TestCase):
    def test_liste_uniquement_les_dons_du_donateur_connecte(self):
        donateur1 = User.objects.create_user(
            username="d1", password="x", role=User.Role.DONATEUR
        )
        donateur2 = User.objects.create_user(
            username="d2", password="x", role=User.Role.DONATEUR
        )
        Don.objects.create(donateur=donateur1, montant=100, type_don=Don.TypeDon.UNIQUE)
        Don.objects.create(donateur=donateur2, montant=200, type_don=Don.TypeDon.UNIQUE)

        self.client.force_login(donateur1)
        response = self.client.get(reverse("dons:mes_dons"), {"periode": "annee"})
        dons_affiches = [entree["don"] for entree in response.context["log"]]
        self.assertEqual(dons_affiches, list(Don.objects.filter(donateur=donateur1)))


class CreerAffectationViewTests(TestCase):
    def setUp(self):
        self.responsable = User.objects.create_user(
            username="resp2",
            password="pass1234",
            role=User.Role.RESPONSABLE,
            email="resp2@example.com",
        )
        self.donateur = User.objects.create_user(
            username="d3",
            password="pass1234",
            role=User.Role.DONATEUR,
            email="d3@example.com",
        )
        self.don = Don.objects.create(
            donateur=self.donateur, montant=1000, type_don=Don.TypeDon.UNIQUE
        )
        self.budget = Budget.objects.create(module=Budget.Module.ECOLE, periode="2026-T1")
        beneficiaire = Beneficiaire.objects.create(nom="A", prenom="B", cin="X1")
        self.demande = DemandeAide.objects.create(
            beneficiaire=beneficiaire,
            titre="Aide",
            categorie=DemandeAide.Categorie.ETUDE,
            description="...",
            urgence=DemandeAide.Urgence.FAIBLE,
            consentement_donnees=True,
        )

    def test_cible_beneficiaire_sans_demande_est_invalide(self):
        self.client.force_login(self.responsable)
        response = self.client.post(
            reverse("dons:creer_affectation"),
            {
                "don": self.don.pk,
                "budget": self.budget.pk,
                "montant_affecte": "100",
                "cible": Affectation.Cible.BENEFICIAIRE,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Affectation.objects.exists())

    def test_affectation_totale_marque_le_don_distribue_et_notifie(self):
        self.client.force_login(self.responsable)
        response = self.client.post(
            reverse("dons:creer_affectation"),
            {
                "don": self.don.pk,
                "budget": self.budget.pk,
                "montant_affecte": "1000",
                "cible": Affectation.Cible.BENEFICIAIRE,
                "demande_aide": self.demande.pk,
            },
        )
        self.assertRedirects(response, reverse("dons:liste_dons"))
        self.don.refresh_from_db()
        self.assertEqual(self.don.statut, Don.Statut.DISTRIBUE)
        self.assertEqual(len(mail.outbox), 1)

    def test_montant_superieur_au_solde_est_invalide(self):
        self.client.force_login(self.responsable)
        response = self.client.post(
            reverse("dons:creer_affectation"),
            {
                "don": self.don.pk,
                "budget": self.budget.pk,
                "montant_affecte": "1500",
                "cible": Affectation.Cible.ECOLE,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Affectation.objects.exists())


class DonDetailViewTests(TestCase):
    def setUp(self):
        self.responsable = User.objects.create_user(
            username="resp3", password="pass1234", role=User.Role.RESPONSABLE
        )
        self.donateur = User.objects.create_user(
            username="d4", password="pass1234", role=User.Role.DONATEUR
        )
        self.don = Don.objects.create(
            donateur=self.donateur, montant=1000, type_don=Don.TypeDon.UNIQUE
        )
        self.budget = Budget.objects.create(module=Budget.Module.ECOLE, periode="2026-T1")

    def test_affiche_les_affectations_du_don(self):
        Affectation.objects.create(
            don=self.don,
            budget=self.budget,
            montant_affecte=300,
            cible=Affectation.Cible.ECOLE,
            validee_par=self.responsable,
        )
        self.client.force_login(self.responsable)
        response = self.client.get(reverse("dons:don_detail", args=[self.don.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_affecte"], 300)
        self.assertEqual(response.context["reste"], 700)
        self.assertEqual(len(response.context["affectations"]), 1)

    def test_don_sans_affectation(self):
        self.client.force_login(self.responsable)
        response = self.client.get(reverse("dons:don_detail", args=[self.don.pk]))
        self.assertEqual(response.context["total_affecte"], 0)
        self.assertEqual(response.context["reste"], 1000)

    def test_acces_refuse_hors_responsable(self):
        self.client.force_login(self.donateur)
        response = self.client.get(reverse("dons:don_detail", args=[self.don.pk]))
        self.assertEqual(response.status_code, 403)


class CategorieImpactTests(TestCase):
    def setUp(self):
        self.donateur = User.objects.create_user(
            username="don5", password="x", role=User.Role.DONATEUR
        )
        beneficiaire = Beneficiaire.objects.create(nom="X", prenom="Y", cin="II1")
        self.demande_etude = DemandeAide.objects.create(
            beneficiaire=beneficiaire, titre="T", categorie=DemandeAide.Categorie.ETUDE,
            description="...", urgence=DemandeAide.Urgence.FAIBLE, consentement_donnees=True,
        )
        self.demande_sante = DemandeAide.objects.create(
            beneficiaire=beneficiaire, titre="T2", categorie=DemandeAide.Categorie.SANTE,
            description="...", urgence=DemandeAide.Urgence.FAIBLE, consentement_donnees=True,
        )

    def test_don_mensuel_est_famille_meme_si_cible(self):
        don = Don.objects.create(
            donateur=self.donateur, montant=100, type_don=Don.TypeDon.MENSUEL,
            demande_aide=self.demande_etude,
        )
        self.assertEqual(categorie_impact(don), "famille")

    def test_don_unique_cible_etude_est_scolaire(self):
        don = Don.objects.create(
            donateur=self.donateur, montant=100, type_don=Don.TypeDon.UNIQUE,
            demande_aide=self.demande_etude,
        )
        self.assertEqual(categorie_impact(don), "scolaire")

    def test_don_unique_cible_sante_est_sante(self):
        don = Don.objects.create(
            donateur=self.donateur, montant=100, type_don=Don.TypeDon.UNIQUE,
            demande_aide=self.demande_sante,
        )
        self.assertEqual(categorie_impact(don), "sante")

    def test_don_unique_sans_cible_est_general(self):
        don = Don.objects.create(
            donateur=self.donateur, montant=100, type_don=Don.TypeDon.UNIQUE,
        )
        self.assertEqual(categorie_impact(don), "general")


class BeneficiairesTouchesTests(TestCase):
    def setUp(self):
        self.donateur = User.objects.create_user(
            username="don6", password="x", role=User.Role.DONATEUR
        )
        self.responsable = User.objects.create_user(
            username="resp4", password="x", role=User.Role.RESPONSABLE
        )
        self.budget = Budget.objects.create(module=Budget.Module.DONS, periode="2026-T1")
        self.beneficiaire_directe = Beneficiaire.objects.create(nom="A", prenom="B", cin="JJ1")
        self.beneficiaire_indirecte = Beneficiaire.objects.create(nom="C", prenom="D", cin="JJ2")
        self.demande_directe = DemandeAide.objects.create(
            beneficiaire=self.beneficiaire_directe, titre="T", categorie=DemandeAide.Categorie.ETUDE,
            description="...", urgence=DemandeAide.Urgence.FAIBLE, consentement_donnees=True,
        )
        self.demande_indirecte = DemandeAide.objects.create(
            beneficiaire=self.beneficiaire_indirecte, titre="T", categorie=DemandeAide.Categorie.ETUDE,
            description="...", urgence=DemandeAide.Urgence.FAIBLE, consentement_donnees=True,
        )

    def test_beneficiaire_atteint_directement_via_don_cible(self):
        Don.objects.create(
            donateur=self.donateur, montant=500, type_don=Don.TypeDon.UNIQUE,
            demande_aide=self.demande_directe,
        )
        resultats = beneficiaires_touches(self.donateur)
        self.assertIn(self.beneficiaire_directe, resultats)
        self.assertNotIn(self.beneficiaire_indirecte, resultats)

    def test_beneficiaire_atteint_via_affectation(self):
        don = Don.objects.create(donateur=self.donateur, montant=500, type_don=Don.TypeDon.UNIQUE)
        Affectation.objects.create(
            don=don, budget=self.budget, montant_affecte=500,
            cible=Affectation.Cible.BENEFICIAIRE, demande_aide=self.demande_indirecte,
            validee_par=self.responsable,
        )
        resultats = beneficiaires_touches(self.donateur)
        self.assertIn(self.beneficiaire_indirecte, resultats)

    def test_dons_non_cibles_ne_comptent_pas(self):
        Don.objects.create(donateur=self.donateur, montant=500, type_don=Don.TypeDon.UNIQUE)
        self.assertEqual(beneficiaires_touches(self.donateur).count(), 0)


class DonneesEspaceDonateurTests(TestCase):
    def test_total_periode_exclut_les_dons_hors_periode(self):
        from datetime import date

        donateur = User.objects.create_user(
            username="don7", password="x", role=User.Role.DONATEUR
        )
        recent = Don.objects.create(donateur=donateur, montant=500, type_don=Don.TypeDon.UNIQUE)
        ancien = Don.objects.create(donateur=donateur, montant=1000, type_don=Don.TypeDon.UNIQUE)
        Don.objects.filter(pk=ancien.pk).update(date_don=date(2020, 1, 1))

        donnees = donnees_espace_donateur(donateur, "mois")
        self.assertEqual(donnees["total_periode"], 500)
        self.assertEqual(donnees["total_all_time"], 1500)
        self.assertEqual(donnees["nb_contributions"], 2)


class MesDonsViewV2Tests(TestCase):
    def setUp(self):
        self.donateur = User.objects.create_user(
            username="don8", password="pass1234", role=User.Role.DONATEUR
        )
        Don.objects.create(donateur=self.donateur, montant=500, type_don=Don.TypeDon.UNIQUE)

    def test_periode_invalide_retombe_sur_6mois(self):
        self.client.force_login(self.donateur)
        response = self.client.get(reverse("dons:mes_dons"), {"periode": "n_importe_quoi"})
        self.assertEqual(response.context["periode"], "6mois")

    def test_export_csv(self):
        self.client.force_login(self.donateur)
        response = self.client.get(reverse("dons:exporter_mes_dons"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")

    def test_recu_pdf(self):
        self.client.force_login(self.donateur)
        response = self.client.get(reverse("dons:recu_fiscal"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
