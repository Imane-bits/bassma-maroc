from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.utils import timezone

from aide.models import Beneficiaire, DemandeAide
from comptabilite.models import Budget, DepenseMensuelle, RecetteMensuelle
from dons.models import Affectation, Don
from ecole.models import Eleve, PaiementScolarite, PreinscriptionEleve
from formation.models import FormationCouture, InscriptionFormation
from personnel.models import Membre

User = get_user_model()

MARKER_CIN = "DEMO-0001"
BENEFICIAIRE_EMAIL = "imanejennane@gmail.com"


class Command(BaseCommand):
    help = "Remplit la base avec des données de démonstration réalistes."

    def handle(self, *args, **options):
        responsable = self._get_or_create_responsable()

        if Beneficiaire.objects.filter(cin=MARKER_CIN).exists():
            self.stdout.write(self.style.WARNING("Des données de démo générales existent déjà."))
        else:
            self._seed_general_demo_data(responsable)

        self._seed_beneficiaire_vitrine(responsable)
        self._seed_comptabilite_detaillee()

        self.stdout.write(self.style.SUCCESS("Terminé."))

    def _get_or_create_responsable(self):
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
        return responsable

    def _seed_general_demo_data(self, responsable):
        today = timezone.localdate()

        donateurs_data = [
            ("Youssef", "Bennis"),
            ("Salma", "Chraibi"),
            ("Karim", "Idrissi"),
            ("Nabil", "Sekkat"),
            ("Amal", "Toumi"),
            ("Fondation", "Al Amal"),
        ]
        donateurs = []
        for i, (prenom, nom) in enumerate(donateurs_data, start=1):
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
        youssef, salma, karim, nabil, amal, fondation = donateurs

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

        # Montants alignés sur ce qu'une affectation réelle va couvrir plus
        # bas (6000/8000/5000 DH), pour que les demandes financées affichent
        # une barre de progression à 100% cohérente avec les dons reçus.
        demandes_data = [
            (beneficiaires[0], "دعم غذائي شهري", DemandeAide.Categorie.NUTRITION,
             DemandeAide.Urgence.HAUTE, DemandeAide.Statut.ACCEPTEE, 6000),
            (beneficiaires[1], "مصاريف طبية عاجلة", DemandeAide.Categorie.SANTE,
             DemandeAide.Urgence.HAUTE, DemandeAide.Statut.ACCEPTEE, 8000),
            (beneficiaires[2], "تمدرس الأبناء", DemandeAide.Categorie.ETUDE,
             DemandeAide.Urgence.MOYENNE, DemandeAide.Statut.EN_ATTENTE, 3500),
            (beneficiaires[3], "مواد خياطة للعمل المنزلي", DemandeAide.Categorie.COUTURE,
             DemandeAide.Urgence.FAIBLE, DemandeAide.Statut.ACCEPTEE, 5000),
            (beneficiaires[4], "مساعدة على السكن", DemandeAide.Categorie.NUTRITION,
             DemandeAide.Urgence.HAUTE, DemandeAide.Statut.REFUSEE, 4500),
            (beneficiaires[0], "دعم لعلاج طبي مزمن", DemandeAide.Categorie.SANTE,
             DemandeAide.Urgence.HAUTE, DemandeAide.Statut.EN_ATTENTE, 7000),
            (beneficiaires[2], "إعادة تأهيل منزل متضرر", DemandeAide.Categorie.NUTRITION,
             DemandeAide.Urgence.MOYENNE, DemandeAide.Statut.EN_COURS, 9000),
            (beneficiaires[4], "تمويل مشروع تجاري صغير", DemandeAide.Categorie.COUTURE,
             DemandeAide.Urgence.FAIBLE, DemandeAide.Statut.ACCEPTEE, 3000),
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
        demande_nutrition, demande_sante, _, demande_couture, *_ = demandes

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

        # Total exactement 284 400 DH ici + 600 DH pour le don de la
        # bénéficiaire vitrine = 285 000 DH, identique à "تبرعات الأفراد"
        # dans la comptabilité détaillée. Les dons ciblant une demande
        # précise (demande_aide déjà renseigné à la création) sont ceux
        # qui alimentent montant_collecte / la barre de progression sur
        # "besoins" -- une Affectation seule ne suffit pas, elle sert
        # uniquement à la redistribution des dons non ciblés (école,
        # centre de formation).
        dons_data = [
            (youssef, 500, None), (salma, 800, None), (karim, 1200, None), (nabil, 300, None),
            (amal, 2000, None), (youssef, 750, None), (salma, 1500, None), (karim, 600, None),
            (nabil, 900, None), (amal, 1000, None),
            (fondation, 100000, None),
            (nabil, 80000, None),
            (karim, 49000, None), (karim, 6000, "nutrition"), (karim, 5000, "couture"),
            (salma, 26850, None), (salma, 8000, "sante"),
        ]
        cibles_par_cle = {
            "nutrition": demande_nutrition,
            "sante": demande_sante,
            "couture": demande_couture,
        }
        dons = []
        for i, (donateur, montant, cle_demande) in enumerate(dons_data):
            don = Don.objects.create(
                donateur=donateur,
                montant=montant,
                type_don=Don.TypeDon.MENSUEL if i % 3 == 0 else Don.TypeDon.UNIQUE,
                demande_aide=cibles_par_cle.get(cle_demande),
            )
            dons.append(don)
        (
            don_fondation, don_nabil_80k, don_karim_pool,
            don_karim_nutrition, don_karim_couture,
            don_salma_pool, don_salma_sante,
        ) = dons[-7:]

        def affecter_et_maj_statut(don, cible, montant_affecte, demande_aide=None, budget=budget_dons):
            Affectation.objects.create(
                don=don,
                budget=budget,
                montant_affecte=montant_affecte,
                cible=cible,
                demande_aide=demande_aide,
                validee_par=responsable,
            )
            total = don.affectations.aggregate(t=Sum("montant_affecte"))["t"] or 0
            don.statut = Don.Statut.DISTRIBUE if total >= don.montant else Don.Statut.EN_AFFECTATION
            don.save(update_fields=["statut"])

        affecter_et_maj_statut(don_fondation, Affectation.Cible.ECOLE, 100000, budget=budget_ecole)
        affecter_et_maj_statut(don_nabil_80k, Affectation.Cible.CENTRE_FORMATION, 80000, budget=budget_formation)
        affecter_et_maj_statut(don_karim_nutrition, Affectation.Cible.BENEFICIAIRE, 6000, demande_aide=demande_nutrition)
        affecter_et_maj_statut(don_karim_couture, Affectation.Cible.BENEFICIAIRE, 5000, demande_aide=demande_couture)
        affecter_et_maj_statut(don_salma_sante, Affectation.Cible.BENEFICIAIRE, 8000, demande_aide=demande_sante)

        eleves_data = [
            ("Bennani", "Yassine", "CE1", "du", 1200),
            ("Chraibi", "Meryem", "CE2", "en_retard", 1500),
            ("Idrissi", "Omar", "CP", "paye", 1000),
            ("Zouiten", "Salma", "CE1", "du", 1200),
            ("Alami", "Adam", "CM1", "en_retard", 1600),
            ("Berrada", "Hiba", "CP", "paye", 1000),
        ]
        for i, (nom, prenom, classe, statut_paiement, montant) in enumerate(eleves_data, start=1):
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
                    "montant": montant,
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

        formation1 = self._get_or_create_formation1()
        formation2 = self._get_or_create_formation2()

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

    def _get_or_create_formation1(self):
        formation1, _ = FormationCouture.objects.get_or_create(
            intitule="Couture débutant",
            defaults={"description": "Initiation à la couture traditionnelle.", "duree_semaines": 8},
        )
        return formation1

    def _get_or_create_formation2(self):
        formation2, _ = FormationCouture.objects.get_or_create(
            intitule="Broderie avancée",
            defaults={"description": "Perfectionnement en broderie marocaine.", "duree_semaines": 12},
        )
        return formation2

    def _seed_beneficiaire_vitrine(self, responsable):
        if Beneficiaire.objects.filter(email=BENEFICIAIRE_EMAIL).exists():
            self.stdout.write(self.style.WARNING("La bénéficiaire vitrine existe déjà."))
            return

        beneficiaire = Beneficiaire.objects.create(
            nom="Jennane",
            prenom="Imane",
            cin="DEMO-VIP1",
            date_naissance=date(1990, 7, 22),
            telephone="0611223344",
            email=BENEFICIAIRE_EMAIL,
            ville="Rabat",
            adresse="حي الرياض، الرباط",
            situation_familiale=Beneficiaire.SituationFamiliale.DIVORCE,
            nombre_enfants=2,
            enfants_scolarises=2,
            probleme_sante=False,
        )

        demande_acceptee = DemandeAide.objects.create(
            beneficiaire=beneficiaire,
            titre="دعم لتمدرس الأبناء",
            categorie=DemandeAide.Categorie.ETUDE,
            description="طلب دعم لتغطية مصاريف التمدرس للموسم الدراسي الحالي.",
            urgence=DemandeAide.Urgence.MOYENNE,
            montant_demande=900,
            consentement_donnees=True,
            statut=DemandeAide.Statut.ACCEPTEE,
        )
        DemandeAide.objects.create(
            beneficiaire=beneficiaire,
            titre="مواد خياطة لبدء نشاط مدر للدخل",
            categorie=DemandeAide.Categorie.COUTURE,
            description="طلب مواد خياطة أساسية لإطلاق مشروع صغير.",
            urgence=DemandeAide.Urgence.FAIBLE,
            montant_demande=500,
            consentement_donnees=True,
            statut=DemandeAide.Statut.EN_ATTENTE,
        )
        DemandeAide.objects.create(
            beneficiaire=beneficiaire,
            titre="مساعدة غذائية استعجالية",
            categorie=DemandeAide.Categorie.NUTRITION,
            description="طلب مساعدة غذائية عاجلة لأسرة تعاني من وضعية صعبة.",
            urgence=DemandeAide.Urgence.HAUTE,
            montant_demande=700,
            consentement_donnees=True,
            statut=DemandeAide.Statut.REFUSEE,
        )

        donateur, _ = User.objects.get_or_create(
            username="demo.donateur.vitrine@example.com",
            defaults={
                "email": "demo.donateur.vitrine@example.com",
                "first_name": "Hicham",
                "last_name": "Berrada",
                "role": User.Role.DONATEUR,
            },
        )
        Don.objects.create(
            donateur=donateur,
            montant=600,
            type_don=Don.TypeDon.UNIQUE,
            demande_aide=demande_acceptee,
        )

        formation1 = self._get_or_create_formation1()
        formation2 = self._get_or_create_formation2()
        InscriptionFormation.objects.create(
            beneficiaire=beneficiaire,
            formation=formation1,
            progression=100,
            statut=InscriptionFormation.Statut.TERMINEE,
        )
        InscriptionFormation.objects.create(
            beneficiaire=beneficiaire,
            formation=formation2,
            progression=25,
            statut=InscriptionFormation.Statut.EN_COURS,
        )

        self.stdout.write(
            self.style.SUCCESS(f"Bénéficiaire vitrine créée ({BENEFICIAIRE_EMAIL}).")
        )

    def _seed_comptabilite_detaillee(self):
        if DepenseMensuelle.objects.exists():
            self.stdout.write(self.style.WARNING("Les données comptables détaillées existent déjà."))
            return

        Programme = DepenseMensuelle.Programme
        depenses_par_mois = {
            date(2026, 3, 1): {Programme.AIDE: 66000, Programme.ECOLE: 42000, Programme.FORMATION: 31000, Programme.ACTIVITES: 20000, Programme.GESTION: 12000},
            date(2026, 4, 1): {Programme.AIDE: 70000, Programme.ECOLE: 44000, Programme.FORMATION: 32000, Programme.ACTIVITES: 24000, Programme.GESTION: 13000},
            date(2026, 5, 1): {Programme.AIDE: 72000, Programme.ECOLE: 45000, Programme.FORMATION: 33000, Programme.ACTIVITES: 23000, Programme.GESTION: 13000},
            date(2026, 6, 1): {Programme.AIDE: 71000, Programme.ECOLE: 44000, Programme.FORMATION: 31000, Programme.ACTIVITES: 25000, Programme.GESTION: 13500},
            date(2026, 7, 1): {Programme.AIDE: 70000, Programme.ECOLE: 45000, Programme.FORMATION: 32000, Programme.ACTIVITES: 22000, Programme.GESTION: 13500},
            date(2026, 8, 1): {Programme.AIDE: 71000, Programme.ECOLE: 45000, Programme.FORMATION: 31000, Programme.ACTIVITES: 21000, Programme.GESTION: 13000},
        }
        for mois, valeurs in depenses_par_mois.items():
            for programme, montant in valeurs.items():
                DepenseMensuelle.objects.create(mois=mois, programme=programme, montant=montant)

        Source = RecetteMensuelle.Source
        totaux_recettes = {
            Source.INDIVIDUS: 285000,
            Source.COOPERATION: 320000,
            Source.INDH: 250000,
            Source.ENTREPRISES: 165000,
            Source.AGR: 90000,
        }
        mois_liste = list(depenses_par_mois.keys())
        for source, total in totaux_recettes.items():
            base = total // len(mois_liste)
            reste = total - base * len(mois_liste)
            for i, mois in enumerate(mois_liste):
                montant = base + reste if i == 0 else base
                RecetteMensuelle.objects.create(mois=mois, source=source, montant=montant)

        self.stdout.write(self.style.SUCCESS("Données comptables détaillées créées."))
