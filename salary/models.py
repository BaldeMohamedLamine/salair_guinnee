from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import secrets
import string
import os

class CustomUserManager(BaseUserManager):
    """Gestionnaire personnalisé pour le modèle User"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Créer et sauvegarder un utilisateur avec l'email donné et le mot de passe"""
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Créer et sauvegarder un superutilisateur avec l'email donné et le mot de passe"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('must_change_password', False)  # Superuser n'a pas besoin de changer le mot de passe

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """Modèle utilisateur personnalisé avec gestion des mots de passe temporaires"""
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    
    must_change_password = models.BooleanField(
        default=True,
        verbose_name="Doit changer le mot de passe",
        help_text="Cochez si l'utilisateur doit changer son mot de passe à la prochaine connexion"
    )
    temporary_password = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        verbose_name="Mot de passe temporaire",
        help_text="Mot de passe temporaire généré automatiquement"
    )
    password_changed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Mot de passe changé le",
        help_text="Date de la dernière modification du mot de passe"
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
    
    def generate_temporary_password(self, length=12):
        """Génère un mot de passe temporaire sécurisé"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        self.temporary_password = password
        self.must_change_password = True
        self.save()
        return password
    
    def mark_password_changed(self):
        """Marque que l'utilisateur a changé son mot de passe"""
        self.must_change_password = False
        self.password_changed_at = timezone.now()
        self.temporary_password = None
        self.save()

class Employee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utilisateur", related_name="employees", null=True, blank=True)
    nom_complet = models.CharField(max_length=200, verbose_name="Nom complet de l'employé")
    date_creation = models.DateTimeField(default=timezone.now, verbose_name="Date de création")
    salaire_net = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Salaire net souhaité")
    
    # Déductions pour le salaire net à payer
    avance_salaire = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Avance sur salaire", default=0)
    saisie_opposition = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Saisie et opposition", default=0)
    salaire_net_a_payer = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Salaire net à payer", default=0)
    
    salaire_base = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Salaire de base calculé")
    salaire_brut = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Salaire brut calculé")
    salaire_imposable = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Salaire imposable calculé")
    cnss_employe = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="CNSS employé (5%)")
    rts = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="RTS (Retenue à la Source)")
    total_charges_employee = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total charges employé")
    cnss_employeur = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="CNSS employeur (18%)")
    versement_forfaitaire = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Versement forfaitaire (6%)")
    taxe_apprentissage = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Taxe d'apprentissage (2%)")
    total_cnss_patronal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total CNSS patronal")
    # Primes taxables
    prime_cherte_vie = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Prime de cherté de vie", default=0)
    indemnite_logement = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Indemnité de logement", default=0)
    indemnite_transport = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Indemnité de transport", default=0)
    indemnite_repas = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Indemnité de repas", default=0)
    prime_responsabilite = models.DecimalField(max_digits=12, decimal_places=2,verbose_name="Prime de responsabilité (taxable)", default=0)
    primes_taxables = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Primes taxables")
    
    # Primes exonérées (non taxables)
    prime_retraite = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Prime de retraite", default=0)
    prime_interim = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Prime d'intérim", default=0)
    prime_anciennete = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Prime d'ancienneté", default=0)
    primes_exonerees = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total primes exonérées", default=0)
    avantage_nature = models.DecimalField(max_digits=12, decimal_places=2,verbose_name="Avantage en nature", default=0)
    ecart_imposable = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Écart imposable")

    class Meta:
        verbose_name = "Employé"
        verbose_name_plural = "Employés"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.nom_complet} - {self.salaire_net:,.0f} GNF"
    
    def get_total_cout_employeur(self):
        """Calcule le coût total pour l'employeur"""
        return self.salaire_brut + self.total_cnss_patronal
    
    def get_rts_details(self):
        """Retourne les détails du calcul RTS pour l'export Excel"""
        from .utils import calculate_rts_detailed
        _, details = calculate_rts_detailed(self.salaire_imposable)
        return details

def logo_upload_path(instance, filename):
    """Génère le chemin de téléchargement pour le logo"""
    ext = filename.split('.')[-1]
    filename = f"logo.{ext}"
    return os.path.join('company', filename)

class Company(models.Model):
    """Modèle pour les informations de l'entreprise"""
    name = models.CharField(max_length=200, verbose_name="Nom de l'entreprise", default="Mon Entreprise")
    logo = models.ImageField(
        upload_to=logo_upload_path,
        verbose_name="Logo de l'entreprise",
        help_text="Téléchargez le logo de votre entreprise (PNG, JPG, JPEG recommandés)",
        blank=True,
        null=True
    )
    address = models.TextField(verbose_name="Adresse", blank=True)
    phone = models.CharField(max_length=20, verbose_name="Téléphone", blank=True)
    email = models.EmailField(verbose_name="Email", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        verbose_name = "Entreprise"
        verbose_name_plural = "Entreprises"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # S'assurer qu'il n'y a qu'une seule instance de Company
        if not self.pk and Company.objects.exists():
            # Si c'est une nouvelle instance et qu'il en existe déjà une, ne pas créer
            return
        super().save(*args, **kwargs)
    
    @classmethod
    def get_company(cls):
        """Retourne l'instance unique de Company ou en crée une"""
        company, created = cls.objects.get_or_create(
            defaults={'name': 'Mon Entreprise'}
        )
        return company