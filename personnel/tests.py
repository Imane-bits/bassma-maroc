from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Membre

User = get_user_model()


class MembreCrudTests(TestCase):
    def setUp(self):
        self.responsable = User.objects.create_user(
            username="resp_personnel", password="pass1234", role=User.Role.RESPONSABLE
        )

    def test_creation_membre(self):
        self.client.force_login(self.responsable)
        response = self.client.post(
            reverse("personnel:creer_membre"),
            {
                "nom": "Alaoui",
                "prenom": "Yassine",
                "poste": "Coordinateur",
                "telephone": "0600000000",
                "email": "yassine@example.com",
                "date_entree": "2024-01-15",
            },
        )
        self.assertRedirects(response, reverse("personnel:liste_membres"))
        membre = Membre.objects.get()
        self.assertEqual(membre.poste, "Coordinateur")
        self.assertEqual(membre.statut, Membre.Statut.ACTIF)

    def test_desactivation_puis_reactivation(self):
        membre = Membre.objects.create(nom="Idrissi", prenom="Sara", poste="Comptable")
        self.client.force_login(self.responsable)

        self.client.post(reverse("personnel:desactiver_membre", args=[membre.pk]))
        membre.refresh_from_db()
        self.assertEqual(membre.statut, Membre.Statut.INACTIF)

        self.client.post(reverse("personnel:activer_membre", args=[membre.pk]))
        membre.refresh_from_db()
        self.assertEqual(membre.statut, Membre.Statut.ACTIF)

    def test_filtre_par_statut(self):
        Membre.objects.create(nom="A", prenom="B", poste="X", statut=Membre.Statut.ACTIF)
        Membre.objects.create(nom="C", prenom="D", poste="Y", statut=Membre.Statut.INACTIF)

        self.client.force_login(self.responsable)
        response = self.client.get(reverse("personnel:liste_membres"), {"statut": "inactif"})
        self.assertEqual(len(response.context["membres"]), 1)
        self.assertEqual(response.context["membres"][0].nom, "C")

    def test_acces_refuse_hors_responsable(self):
        donateur = User.objects.create_user(
            username="don_personnel", password="pass1234", role=User.Role.DONATEUR
        )
        self.client.force_login(donateur)
        response = self.client.get(reverse("personnel:liste_membres"))
        self.assertEqual(response.status_code, 403)
