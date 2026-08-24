from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from comptabilite.models import Budget

from .models import Eleve, PaiementScolarite, PreinscriptionEleve

User = get_user_model()


class ListePaiementsViewTests(TestCase):
    def setUp(self):
        self.responsable = User.objects.create_user(
            username="resp3", password="pass1234", role=User.Role.RESPONSABLE
        )
        tuteur = User.objects.create_user(
            username="tut1", password="x", role=User.Role.DONATEUR
        )
        self.eleve = Eleve.objects.create(
            tuteur=tuteur,
            nom="Bennani",
            prenom="Yassine",
            date_naissance="2015-01-01",
            classe="CE1",
            tuteur_nom="Bennani",
            tuteur_contact="0600000000",
        )
        self.budget = Budget.objects.create(module=Budget.Module.ECOLE, periode="2026-T1")

    def test_paiement_du_en_retard_est_auto_reclassifie(self):
        paiement = PaiementScolarite.objects.create(
            eleve=self.eleve,
            budget=self.budget,
            montant=500,
            date_echeance=timezone.localdate() - timedelta(days=1),
            statut_paiement=PaiementScolarite.StatutPaiement.DU,
        )
        self.client.force_login(self.responsable)
        self.client.get(reverse("ecole:liste_paiements"))

        paiement.refresh_from_db()
        self.assertEqual(paiement.statut_paiement, PaiementScolarite.StatutPaiement.EN_RETARD)

    def test_paiement_futur_reste_du(self):
        paiement = PaiementScolarite.objects.create(
            eleve=self.eleve,
            budget=self.budget,
            montant=500,
            date_echeance=timezone.localdate() + timedelta(days=5),
            statut_paiement=PaiementScolarite.StatutPaiement.DU,
        )
        self.client.force_login(self.responsable)
        self.client.get(reverse("ecole:liste_paiements"))

        paiement.refresh_from_db()
        self.assertEqual(paiement.statut_paiement, PaiementScolarite.StatutPaiement.DU)

    def test_marquer_paye(self):
        paiement = PaiementScolarite.objects.create(
            eleve=self.eleve,
            budget=self.budget,
            montant=500,
            date_echeance=timezone.localdate() + timedelta(days=5),
        )
        self.client.force_login(self.responsable)
        response = self.client.post(reverse("ecole:marquer_paye", args=[paiement.pk]))
        self.assertRedirects(response, reverse("ecole:liste_paiements"))
        paiement.refresh_from_db()
        self.assertEqual(paiement.statut_paiement, PaiementScolarite.StatutPaiement.PAYE)

    def test_acces_refuse_hors_responsable(self):
        donateur = User.objects.create_user(
            username="don9", password="x", role=User.Role.DONATEUR
        )
        self.client.force_login(donateur)
        response = self.client.get(reverse("ecole:liste_paiements"))
        self.assertEqual(response.status_code, 403)


class PreinscrireViewTests(TestCase):
    def _valid_data(self, **overrides):
        data = {
            "nom_enfant": "Bennani",
            "prenom_enfant": "Yassine",
            "date_naissance": "2020-05-01",
            "tuteur_nom": "Karim Bennani",
            "tuteur_contact": "0600000000",
            "adresse": "Casablanca",
        }
        data.update(overrides)
        return data

    def test_soumission_cree_une_preinscription_avec_numero_dossier(self):
        response = self.client.post(reverse("ecole:preinscrire"), self._valid_data())
        preinscription = PreinscriptionEleve.objects.get()
        self.assertRedirects(
            response,
            reverse("ecole:confirmation", args=[preinscription.numero_dossier]),
        )
        self.assertTrue(preinscription.numero_dossier.startswith("PRE-"))
        self.assertEqual(preinscription.statut, PreinscriptionEleve.Statut.EN_ATTENTE)

    def test_donnees_manquantes_rejettent_la_soumission(self):
        data = self._valid_data()
        del data["tuteur_contact"]
        response = self.client.post(reverse("ecole:preinscrire"), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(PreinscriptionEleve.objects.exists())


class SuiviPreinscriptionViewTests(TestCase):
    def setUp(self):
        self.preinscription = PreinscriptionEleve.objects.create(
            nom_enfant="Bennani",
            prenom_enfant="Yassine",
            date_naissance="2020-05-01",
            tuteur_nom="Karim Bennani",
            tuteur_contact="0600000000",
        )

    def test_numero_valide_affiche_la_preinscription(self):
        response = self.client.post(
            reverse("ecole:suivi_preinscription"),
            {"numero_dossier": self.preinscription.numero_dossier},
        )
        self.assertEqual(response.context["preinscription"], self.preinscription)

    def test_numero_inconnu_naffiche_rien(self):
        response = self.client.post(
            reverse("ecole:suivi_preinscription"), {"numero_dossier": "PRE-0000-000000"}
        )
        self.assertIsNone(response.context["preinscription"])


class DecisionPreinscriptionViewTests(TestCase):
    def setUp(self):
        self.responsable = User.objects.create_user(
            username="resp5", password="pass1234", role=User.Role.RESPONSABLE
        )
        self.preinscription = PreinscriptionEleve.objects.create(
            nom_enfant="Bennani",
            prenom_enfant="Yassine",
            date_naissance="2020-05-01",
            tuteur_nom="Karim Bennani",
            tuteur_contact="0600000000",
        )

    def test_acceptation_change_le_statut(self):
        self.client.force_login(self.responsable)
        response = self.client.post(
            reverse("ecole:accepter_preinscription", args=[self.preinscription.pk])
        )
        self.assertRedirects(response, reverse("ecole:liste_preinscriptions"))
        self.preinscription.refresh_from_db()
        self.assertEqual(self.preinscription.statut, PreinscriptionEleve.Statut.ACCEPTEE)

    def test_refus_change_le_statut(self):
        self.client.force_login(self.responsable)
        response = self.client.post(
            reverse("ecole:refuser_preinscription", args=[self.preinscription.pk])
        )
        self.assertRedirects(response, reverse("ecole:liste_preinscriptions"))
        self.preinscription.refresh_from_db()
        self.assertEqual(self.preinscription.statut, PreinscriptionEleve.Statut.REFUSEE)

    def test_acces_refuse_hors_responsable(self):
        donateur = User.objects.create_user(
            username="don10", password="x", role=User.Role.DONATEUR
        )
        self.client.force_login(donateur)
        response = self.client.get(reverse("ecole:liste_preinscriptions"))
        self.assertEqual(response.status_code, 403)
