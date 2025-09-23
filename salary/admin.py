from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django import forms
from django.shortcuts import redirect
from .models import User, Employee, Company
from .auth_views import send_user_credentials

class CustomUserCreationForm(forms.ModelForm):
    """Formulaire de création d'utilisateur personnalisé"""
    email = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(max_length=150, required=False, label="Prénom")
    last_name = forms.CharField(max_length=150, required=False, label="Nom")
    is_staff = forms.BooleanField(required=False, label="Staff status", help_text="Designates whether the user can log into this admin site.")
    is_superuser = forms.BooleanField(required=False, label="Superuser status", help_text="Designates that this user has all permissions without explicitly assigning them.")
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'is_staff', 'is_superuser')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_staff = self.cleaned_data['is_staff']
        user.is_superuser = self.cleaned_data['is_superuser']
        if commit:
            user.save()
        return user

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Administration personnalisée des utilisateurs"""
    
    add_form = CustomUserCreationForm
    
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'must_change_password', 'password_status', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'must_change_password', 'date_joined')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email',)}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Gestion des mots de passe', {
            'fields': ('must_change_password', 'password_changed_at'),
            'classes': ('collapse',)
        }),
        ('Dates importantes', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'is_staff', 'is_superuser'),
        }),
    )
    
    readonly_fields = ('password_changed_at', 'date_joined', 'last_login')
    
    def get_form(self, request, obj=None, **kwargs):
        """Utilise le formulaire de création personnalisé pour les nouveaux utilisateurs"""
        defaults = {}
        if obj is None:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)
    
    def password_status(self, obj):
        """Affiche le statut du mot de passe"""
        if obj.must_change_password:
            return format_html(
                '<span style="color: #e74c3c; font-weight: bold;">⚠️ Doit changer</span>'
            )
        else:
            return format_html(
                '<span style="color: #27ae60; font-weight: bold;">✅ Changé</span>'
            )
    password_status.short_description = 'Statut Mot de Passe'
    
    def save_model(self, request, obj, form, change):
        """Sauvegarde personnalisée avec génération de mot de passe"""
        if not change:  # Nouvel utilisateur
            # Générer un mot de passe temporaire
            import secrets
            import string
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
            temporary_password = ''.join(secrets.choice(alphabet) for _ in range(12))
            
            # Définir le mot de passe temporaire
            obj.set_password(temporary_password)
            obj.must_change_password = True
            
            # Sauvegarder l'utilisateur
            super().save_model(request, obj, form, change)
            
            # Envoyer l'email avec les identifiants
            if obj.email:
                try:
                    from .auth_views import send_user_credentials
                    success = send_user_credentials(obj, temporary_password, request)
                    
                    if success:
                        messages.success(
                            request, 
                            f"✅ Utilisateur créé avec succès ! Email envoyé à {obj.email}"
                        )
                    else:
                        messages.warning(
                            request, 
                            f"⚠️ Utilisateur créé mais échec de l'envoi d'email à {obj.email}"
                        )
                except Exception as e:
                    messages.warning(
                        request, 
                        f"⚠️ Utilisateur créé mais erreur email: {str(e)}"
                    )
            else:
                messages.warning(
                    request, 
                    "⚠️ Utilisateur créé mais aucun email configuré"
                )
        else:
            super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        """Optimiser les requêtes"""
        return super().get_queryset(request).select_related()

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Administration des employés"""
    
    list_display = ('nom_complet', 'salaire_net', 'salaire_brut', 'get_total_cout_employeur', 'date_creation')
    list_filter = ('date_creation',)
    search_fields = ('nom_complet',)
    ordering = ('-date_creation',)
    readonly_fields = ('date_creation',)
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('nom_complet', 'salaire_net', 'date_creation')
        }),
        ('Calculs automatiques', {
            'fields': (
                'salaire_base', 'salaire_brut', 'salaire_imposable',
                'cnss_employe', 'rts', 'total_charges_employee',
                'cnss_employeur', 'versement_forfaitaire', 'taxe_apprentissage',
                'total_cnss_patronal', 'ecart_imposable'
            ),
            'classes': ('collapse',)
        }),
        ('Primes détaillées', {
            'fields': (
                'prime_cherte_vie', 'prime_craie', 'indemnite_logement',
                'indemnite_transport', 'indemnite_repas', 'autre_gratification',
                'primes_taxables_25'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimiser les requêtes"""
        return super().get_queryset(request)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """Administration pour le modèle Company"""
    list_display = ('name', 'has_logo', 'phone', 'email', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'email', 'phone')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'logo')
        }),
        ('Contact', {
            'fields': ('address', 'phone', 'email')
        }),
    )
    
    def has_logo(self, obj):
        """Affiche si l'entreprise a un logo"""
        if obj.logo:
            return format_html(
                '<span style="color: #27ae60; font-weight: bold;">✅ Logo présent</span>'
            )
        else:
            return format_html(
                '<span style="color: #e74c3c; font-weight: bold;">❌ Aucun logo</span>'
            )
    has_logo.short_description = 'Logo'
    
    def has_add_permission(self, request):
        """Empêche l'ajout de plusieurs instances"""
        return not Company.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Empêche la suppression de l'instance"""
        return False
    
    def changelist_view(self, request, extra_context=None):
        """Redirige vers la modification si une instance existe"""
        if Company.objects.exists():
            company = Company.objects.first()
            return redirect(f'../company/{company.id}/change/')
        return super().changelist_view(request, extra_context)