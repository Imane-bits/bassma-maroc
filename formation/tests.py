from django.test import TestCase

from aide.models import Beneficiaire

from .models import FormationCouture, InscriptionFormation


class InscriptionFormationTests(TestCase):
    def setUp(self):
        self.beneficiaire = Beneficiaire.objects.create(
            nom="Amrani", prenom="Sara", cin="AB123456"
        )
        self.formation = FormationCouture.objects.create(
            intitule="Couture débutant", description="...", duree_semaines=8
        )

    def test_numero_inscription_auto_genere_et_unique(self):
        inscription1 = InscriptionFormation.objects.create(
            beneficiaire=self.beneficiaire, formation=self.formation
        )
        inscription2 = InscriptionFormation.objects.create(
            beneficiaire=self.beneficiaire, formation=self.formation
        )
        self.assertTrue(inscription1.numero_inscription.startswith("INS-"))
        self.assertNotEqual(inscription1.numero_inscription, inscription2.numero_inscription)

    def test_passage_a_terminee_genere_une_certification(self):
        inscription = InscriptionFormation.objects.create(
            beneficiaire=self.beneficiaire, formation=self.formation, progression=100
        )
        self.assertFalse(hasattr(inscription, "certification"))

        inscription.statut = InscriptionFormation.Statut.TERMINEE
        inscription.save()

        inscription.refresh_from_db()
        self.assertTrue(hasattr(inscription, "certification"))
        self.assertTrue(inscription.certification.numero.startswith("CERT-"))

    def test_pas_de_double_certification_si_resave(self):
        inscription = InscriptionFormation.objects.create(
            beneficiaire=self.beneficiaire,
            formation=self.formation,
            statut=InscriptionFormation.Statut.TERMINEE,
        )
        numero_initial = inscription.certification.numero

        inscription.progression = 100
        inscription.save()

        inscription.refresh_from_db()
        self.assertEqual(inscription.certification.numero, numero_initial)
