from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class RoleBasedLoginViewTests(TestCase):
    def setUp(self):
        self.responsable = User.objects.create_user(
            username="resp@example.com",
            email="resp@example.com",
            password="pass1234",
            role=User.Role.RESPONSABLE,
        )
        self.donateur = User.objects.create_user(
            username="don@example.com",
            email="don@example.com",
            password="pass1234",
            role=User.Role.DONATEUR,
        )

    def test_responsable_redirige_vers_son_espace(self):
        response = self.client.post(
            reverse("login"), {"username": "resp@example.com", "password": "pass1234"}
        )
        self.assertRedirects(response, reverse("espace_responsable"))

    def test_donateur_redirige_vers_son_espace(self):
        response = self.client.post(
            reverse("login"), {"username": "don@example.com", "password": "pass1234"}
        )
        self.assertRedirects(response, reverse("dons:mes_dons"))

    def test_next_est_respecte_malgre_le_role(self):
        response = self.client.post(
            reverse("login") + "?next=/aide/responsable/beneficiaires/",
            {"username": "resp@example.com", "password": "pass1234"},
        )
        self.assertRedirects(response, "/aide/responsable/beneficiaires/")
