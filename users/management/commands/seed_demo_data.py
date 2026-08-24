from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from aide.models import Beneficiaire, DemandeAide
from comptabilite.models import Budget
from dons.models import Affectation, Don
from ecole.models import Eleve, PaiementScolarite, PreinscriptionEleve
from formation.models import FormationCouture, InscriptionFormation
from personnel.models import Membre

User = get_user_model()

MARKER_CIN = "DEMO-0001"


class Command(BaseCommand):
    help = "Remplit la base avec des données de démonstration réalistes."

    def handle(self, *args, **options):
        if Beneficiaire.objects.filter(cin=MARKER_CIN).exists():
            self.stdout.write(self.style.WARNING("Des données de démo existent déjà — rien à faire."))
            return

        today = timezone.localdate()

        responsable = User.objects.filter(
            role=User.Role.RESPONSABLE, is_active=True
        ).first()
        if responsable is None:
            responsable = User.objects.create_user(
                username="demo.responsable@example.com",
                email="demo.responsable@example.com",
                password="DemoPass123!",
                role=User.Role.RESPONSABLE,
            )

        donateurs = []
        for i, (prenom, nom) in enumerate(
            [("Youssef", "Bennis"), ("Salma", "Chraibi"), ("Karim", "Idrissi")], start=1
        ):
            u, _ = User.objects.get_or_create(
                username=f"demo.donateur{i}@example.com",
                defaults={
                    "email": f"demo.donateur{i}@example.com",
                    "first_name": prenom,
                    "last_name": nom,
                    "role": User.Role.DONATEUR,
                },
            )
            donateurs.append(u)

        beneficiaires_data = [
            ("Amrani", "Fatima", "DEMO-0001", "Casablanca", 3, 2),
            ("Ouali", "Nadia", "DEMO-0002", "Salé", 2, 1),
            ("Bouzid", "Rachid", "DEMO-0003", "Témara", 4, 3),
            ("El Fassi", "Khadija", "DEMO-0004", "Rabat", 1, 1),
            ("Marzouki", "Aïcha", "DEMO-0005", "Sidi Kacem", 5, 2),
        ]
        beneficiaires = []
        for nom, prenom, cin, ville, nb_enfants, nb_scolarises in beneficiaires_data:
            b, _ = Beneficiaire.objects.get_or_create(
                cin=cin,
                defaults={
                    "nom": nom,
                    "prenom": prenom,
                    "date_naissance": date(1985, 3, 12),
                    "telephone": "0600000000",
                    "ville": ville,
                    "adresse": f"حي النور، {ville}",
                    "situation_familiale": Beneficiaire.SituationFamiliale.MARIE,
                    "nombre_enfants": nb_enfants,
                    "enfants_scolarises": nb_scolarises,
                    "probleme_sante": False,
                },
            )
            beneficiaires.append(b)

        demandes_data = [
            (beneficiaires[0], "دعم غذائي شهري", DemandeAide.Categorie.NUTRITION,
             DemandeAide.Urgence.HAUTE, DemandeAide.Statut.EN_ATTENTE, 800),
            (beneficiaires[1], "مصاريف طبية عاجلة", DemandeAide.Categorie.SANTE,
             DemandeAide.Urgence.HAUTE, DemandeAide.Statut.ACCEPTEE, 1500),
            (beneficiaires[2], "تمدرس الأبناء", DemandeAide.Categorie.ETUDE,
             DemandeAide.Urgence.MOYENNE, DemandeAide.Statut.EN_ATTENTE, 600),
            (beneficiaires[3], "مواد خياطة للعمل المنزلي", DemandeAide.Categorie.COUTURE,
             DemandeAide.Urgence.FAIBLE, DemandeAide.Statut.ACCEPTEE, 400),
            (beneficiaires[4], "مساعدة على السكن", DemandeAide.Categorie.NUTRITION,
             DemandeAide.Urgence.HAUTE, DemandeAide.Statut.REFUSEE, 1200),
        ]
        demandes = []
        for beneficiaire, titre, categorie, urgence, statut, montant in demandes_data:
            d = DemandeAide.objects.create(
                beneficiaire=beneficiaire,
                titre=titre,
                categorie=categorie,
                description=f"{titre} — طلب تجريبي لعرض الواجهة.",
                urgence=urgence,
                montant_demande=montant,
                consentement_donnees=True,
                statut=statut,
            )
            demandes.append(d)

        budget_ecole, _ = Budget.objects.get_or_create(
            module=Budget.Module.ECOLE, periode="2026-T1",
            defaults={"recettes": 12000, "depenses": 4500},
        )
        budget_formation, _ = Budget.objects.get_or_create(
            module=Budget.Module.CENTRE_FORMATION, periode="2026-T1",
            defaults={"recettes": 6000, "depenses": 2000},
        )
        budget_dons, _ = Budget.objects.get_or_create(
            module=Budget.Module.DONS, periode="2026-T1",
            defaults={"recettes": 18500, "depenses": 9000},
        )
        Budget.objects.get_or_create(
            module=Budget.Module.GLOBAL, periode="2026-T1",
            defaults={"recettes": 36500, "depenses": 15500},
        )

        dons = []
        montants = [500, 1000, 250, 2000, 750]
        for i, montant in enumerate(montants):
            don = Don.objects.create(
                donateur=donateurs[i % len(donateurs)],
                montant=montant,
                type_don=Don.TypeDon.UNIQUE if i % 2 == 0 else Don.TypeDon.MENSUEL,
                demande_aide=demandes[1] if i == 1 else None,
            )
            dons.append(don)

        Affectation.objects.get_or_create(
            don=dons[0],
            cible=Affectation.Cible.ECOLE,
            defaults={
                "budget": budget_ecole,
                "montant_affecte": dons[0].montant,
                "validee_par": responsable,
            },
        )
        Affectation.objects.get_or_create(
            don=dons[1],
            cible=Affectation.Cible.BENEFICIAIRE,
            demande_aide=demandes[1],
            defaults={
                "budget": budget_dons,
                "montant_affecte": dons[1].montant,
                "validee_par": responsable,
            },
        )
        dons[0].statut = Don.Statut.DISTRIBUE
        dons[0].save(update_fields=["statut"])
        dons[1].statut = Don.Statut.DISTRIBUE
        dons[1].save(update_fields=["statut"])

        eleves_data = [
            ("Bennani", "Yassine", "CE1", "du"),
            ("Chraibi", "Meryem", "CE2", "en_retard"),
            ("Idrissi", "Omar", "CP", "paye"),
        ]
        for i, (nom, prenom, classe, statut_paiement) in enumerate(eleves_data, start=1):
            tuteur, _ = User.objects.get_or_create(
                username=f"demo.tuteur{i}@example.com",
                defaults={
                    "email": f"demo.tuteur{i}@example.com",
                    "role": User.Role.DONATEUR,
                },
            )
            eleve, _ = Eleve.objects.get_or_create(
                tuteur=tuteur,
                defaults={
                    "nom": nom,
                    "prenom": prenom,
                    "date_naissance": date(2017, 6, 1),
                    "classe": classe,
                    "tuteur_nom": f"{prenom} {nom}",
                    "tuteur_contact": "0600000000",
                },
            )
            echeance = (
                today - timedelta(days=10)
                if statut_paiement == "en_retard"
                else today + timedelta(days=20)
            )
            PaiementScolarite.objects.get_or_create(
                eleve=eleve,
                budget=budget_ecole,
                defaults={
                    "montant": 500,
                    "date_echeance": echeance,
                    "statut_paiement": statut_paiement,
                },
            )

        preinscriptions_data = [
            ("Alaoui", "Sofia", PreinscriptionEleve.Statut.EN_ATTENTE),
            ("Berrada", "Adam", PreinscriptionEleve.Statut.ACCEPTEE),
            ("Fassi", "Lina", PreinscriptionEleve.Statut.EN_ATTENTE),
        ]
        for nom, prenom, statut in preinscriptions_data:
            PreinscriptionEleve.objects.create(
                nom_enfant=nom,
                prenom_enfant=prenom,
                date_naissance=date(2020, 4, 10),
                tuteur_nom=f"ولي {prenom}",
                tuteur_contact="0600000000",
                adresse="الرباط",
                statut=statut,
            )

        formation1, _ = FormationCouture.objects.get_or_create(
            intitule="Couture débutant",
            defaults={"description": "Initiation à la couture traditionnelle.", "duree_semaines": 8},
        )
        formation2, _ = FormationCouture.objects.get_or_create(
            intitule="Broderie avancée",
            defaults={"description": "Perfectionnement en broderie marocaine.", "duree_semaines": 12},
        )

        inscriptions_data = [
            (beneficiaires[0], formation1, 40, InscriptionFormation.Statut.EN_COURS),
            (beneficiaires[1], formation1, 100, InscriptionFormation.Statut.TERMINEE),
            (beneficiaires[2], formation2, 10, InscriptionFormation.Statut.EN_COURS),
        ]
        for beneficiaire, formation, progression, statut in inscriptions_data:
            InscriptionFormation.objects.create(
                beneficiaire=beneficiaire,
                formation=formation,
                progression=progression,
                statut=statut,
            )

        membres_data = [
            ("Tazi", "Hind", "منسقة برامج", "actif"),
            ("Amine", "Bilal", "محاسب", "actif"),
            ("Sqalli", "Nawal", "مسؤولة التواصل", "actif"),
            ("Kadiri", "Hamza", "متطوع", "inactif"),
        ]
        for nom, prenom, poste, statut in membres_data:
            Membre.objects.get_or_create(
                nom=nom,
                prenom=prenom,
                defaults={
                    "poste": poste,
                    "telephone": "0600000000",
                    "email": f"{prenom.lower()}.{nom.lower()}@bassmamaroc.local",
                    "date_entree": today - timedelta(days=200),
                    "statut": statut,
                },
            )

        self.stdout.write(self.style.SUCCESS("Données de démonstration créées avec succès."))
