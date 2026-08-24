import random

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Beneficiaire(models.Model):
    class SituationFamiliale(models.TextChoices):
        MARIE = "marie", _("متزوج(ة)")
        CELIBATAIRE = "celibataire", _("أعزب / عزباء")
        VEUF = "veuf", _("أرمل(ة)")
        DIVORCE = "divorce", _("مطلّق(ة)")

    nom = models.CharField(_("nom"), max_length=100, default="")
    prenom = models.CharField(_("prénom"), max_length=100, default="")
    cin = models.CharField(_("CIN"), max_length=20, unique=True, null=True, blank=True)
    date_naissance = models.DateField(_("date de naissance"), null=True, blank=True)
    telephone = models.CharField(_("téléphone"), max_length=20, blank=True)
    email = models.EmailField(_("البريد الإلكتروني"), blank=True)
    ville = models.CharField(_("ville"), max_length=100, blank=True)
    adresse = models.TextField(_("adresse"), blank=True)
    situation_familiale = models.CharField(
        _("situation familiale"), max_length=30, choices=SituationFamiliale.choices, blank=True
    )
    nombre_enfants = models.PositiveSmallIntegerField(_("nombre d'enfants"), default=0)
    enfants_scolarises = models.PositiveSmallIntegerField(_("enfants scolarisés"), default=0)
    probleme_sante = models.BooleanField(
        _("Un membre de la famille a un problème de santé"), default=False
    )

    def __str__(self):
        return f"{self.prenom} {self.nom}"


def generer_numero_dossier():
    annee = timezone.now().year
    while True:
        candidat = f"DOS-{annee}-{random.randint(0, 999999):06d}"
        if not DemandeAide.objects.filter(numero_dossier=candidat).exists():
            return candidat


class DemandeAide(models.Model):
    class Urgence(models.TextChoices):
        FAIBLE = "faible", _("عادي")
        MOYENNE = "moyenne", _("مستعجل")
        HAUTE = "haute", _("مستعجل جدًا")

    class Statut(models.TextChoices):
        EN_ATTENTE = "en_attente", _("قيد الانتظار")
        EN_COURS = "en_cours", _("قيد المعالجة")
        ACCEPTEE = "acceptee", _("مقبولة")
        REFUSEE = "refusee", _("مرفوضة")

    class Categorie(models.TextChoices):
        ETUDE = "etude", _("الدراسة والتمدرس")
        NUTRITION = "nutrition", _("التغذية")
        SANTE = "sante", _("الصحة")
        COUTURE = "couture", _("مواد الخياطة")

    numero_dossier = models.CharField(
        _("numéro de dossier"), max_length=20, unique=True, blank=True
    )
    beneficiaire = models.ForeignKey(
        Beneficiaire, on_delete=models.CASCADE, related_name="demandes_aide"
    )
    titre = models.CharField(_("titre de la demande"), max_length=150, default="")
    categorie = models.CharField(_("catégorie"), max_length=15, choices=Categorie.choices)
    description = models.TextField(_("description"))
    urgence = models.CharField(_("urgence"), max_length=10, choices=Urgence.choices)
    montant_demande = models.DecimalField(
        _("montant demandé"), max_digits=10, decimal_places=2, null=True, blank=True
    )
    consentement_donnees = models.BooleanField(
        _("J'accepte le traitement de mes données personnelles (loi 09-08)"),
        default=False,
    )
    statut = models.CharField(
        _("statut"), max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE
    )
    date_soumission = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.numero_dossier:
            self.numero_dossier = generer_numero_dossier()
        super().save(*args, **kwargs)

    @property
    def montant_collecte(self):
        from django.db.models import Sum

        return self.dons_cibles.aggregate(total=Sum("montant"))["total"] or 0

    def __str__(self):
        return f"{self.numero_dossier} ({self.statut})"


class PieceJustificative(models.Model):
    demande = models.ForeignKey(
        DemandeAide, on_delete=models.CASCADE, related_name="pieces"
    )
    fichier = models.FileField(upload_to="pieces_justificatives/%Y/%m/")
    date_ajout = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.fichier.name
