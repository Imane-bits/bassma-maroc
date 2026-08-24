from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Beneficiaire, DemandeAide

User = get_user_model()


def _demande_de_base(beneficiaire, **overrides):
    data = dict(
        beneficiaire=beneficiaire,
        titre="Besoin de soutien",
        categorie=DemandeAide.Categorie.ETUDE,
        description="Description détaillée.",
        urgence=DemandeAide.Urgence.FAIBLE,
        consentement_donnees=True,
    )
    data.update(overrides)
    return DemandeAide.objects.create(**data)


class SoumettreDemandeViewTests(TestCase):
    def _valid_data(self, **overrides):
        data = {
            "nom_complet": "Fatima Zahra",
            "cin": "CD123456",
            "telephone": "0600000000",
            "ville": "Rabat",
            "nombre_enfants": 2,
            "enfants_scolarises": 1,
            "titre": "Besoin de soutien",
            "categorie": DemandeAide.Categorie.ETUDE,
            "urgence": DemandeAide.Urgence.MOYENNE,
            "description": "Description détaillée.",
            "consentement_donnees": True,
        }
        data.update(overrides)
        return data

    def test_soumission_cree_beneficiaire_et_demande_avec_numero_dossier(self):
        response = self.client.post(reverse("aide:soumettre_demande"), self._valid_data())
        demande = DemandeAide.objects.get()
        self.assertRedirects(
            response, reverse("aide:confirmation", args=[demande.numero_dossier])
        )
        self.assertTrue(demande.numero_dossier.startswith("DOS-"))
        self.assertEqual(demande.beneficiaire.prenom, "Fatima")
        self.assertEqual(demande.beneficiaire.nom, "Zahra")

    def test_meme_cin_reutilise_le_beneficiaire_existant(self):
        self.client.post(
            reverse("aide:soumettre_demande"), self._valid_data(titre="Première demande")
        )
        self.client.post(
            reverse("aide:soumettre_demande"), self._valid_data(titre="Deuxième demande")
        )

        self.assertEqual(Beneficiaire.objects.count(), 1)
        self.assertEqual(DemandeAide.objects.count(), 2)

    def test_sans_consentement_la_demande_est_rejetee(self):
        data = self._valid_data()
        del data["consentement_donnees"]
        response = self.client.post(reverse("aide:soumettre_demande"), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(DemandeAide.objects.exists())


class SuiviDossierViewTests(TestCase):
    def setUp(self):
        beneficiaire = Beneficiaire.objects.create(nom="X", prenom="Y", cin="EE1")
        self.demande = _demande_de_base(beneficiaire)

    def test_numero_valide_affiche_la_demande(self):
        response = self.client.post(
            reverse("aide:suivi_dossier"), {"numero_dossier": self.demande.numero_dossier}
        )
        self.assertEqual(response.context["demande"], self.demande)

    def test_numero_inconnu_naffiche_rien(self):
        response = self.client.post(
            reverse("aide:suivi_dossier"), {"numero_dossier": "DOS-0000-000000"}
        )
        self.assertIsNone(response.context["demande"])


class ListeBesoinsViewTests(TestCase):
    def test_seules_les_demandes_acceptees_avec_montant_sont_affichees(self):
        beneficiaire = Beneficiaire.objects.create(nom="X", prenom="Y", cin="FF1")
        visible = _demande_de_base(
            beneficiaire,
            titre="Visible",
            statut=DemandeAide.Statut.ACCEPTEE,
            montant_demande=500,
        )
        _demande_de_base(
            beneficiaire,
            titre="En attente",
            statut=DemandeAide.Statut.EN_ATTENTE,
            montant_demande=500,
        )
        response = self.client.get(reverse("aide:liste_besoins"))
        self.assertEqual(list(response.context["besoins"]), [visible])


class DecisionDemandeViewTests(TestCase):
    def setUp(self):
        self.responsable = User.objects.create_user(
            username="resp4", password="pass1234", role=User.Role.RESPONSABLE
        )
        beneficiaire = Beneficiaire.objects.create(nom="X", prenom="Y", cin="GG1")
        self.demande = _demande_de_base(beneficiaire)

    def test_acceptation_change_le_statut(self):
        self.client.force_login(self.responsable)
        response = self.client.post(reverse("aide:accepter_demande", args=[self.demande.pk]))
        self.assertRedirects(response, reverse("aide:liste_demandes"))
        self.demande.refresh_from_db()
        self.assertEqual(self.demande.statut, DemandeAide.Statut.ACCEPTEE)

    def test_refus_change_le_statut(self):
        self.client.force_login(self.responsable)
        response = self.client.post(reverse("aide:refuser_demande", args=[self.demande.pk]))
        self.assertRedirects(response, reverse("aide:liste_demandes"))
        self.demande.refresh_from_db()
        self.assertEqual(self.demande.statut, DemandeAide.Statut.REFUSEE)

    def test_acces_refuse_pour_visiteur_non_connecte(self):
        response = self.client.post(reverse("aide:accepter_demande", args=[self.demande.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)
