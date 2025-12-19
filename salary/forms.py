from django import forms

class NetToGrossForm(forms.Form):
    # Nom complet de l'employé
    nom_complet = forms.CharField(
        label="Nom complet de l'employé",
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Prénom et nom de famille',
            'required': True
        }),
        help_text="Saisissez le prénom et nom de famille de l'employé"
    )
    
    # Salaire net souhaité
    net_salary = forms.DecimalField(
        label="Salaire net souhaité",
        min_value=0,
        decimal_places=2,
        max_digits=12,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Entrez le salaire net souhaité'})
    )
    
    # Question sur les primes exonérées
    has_exempt_primes = forms.BooleanField(
        label="Avez-vous des primes exonérées ?",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'has_exempt_primes'})
    )
    
    # Primes exonérées (non taxables)
    prime_retraite = forms.BooleanField(
        label="Prime de retraite",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input exempt-prime', 'disabled': True})
    )
    
    prime_interim = forms.BooleanField(
        label="Prime d'intérim",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input exempt-prime', 'disabled': True})
    )
    
    prime_anciennete = forms.BooleanField(
        label="Prime d'ancienneté",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input exempt-prime', 'disabled': True})
    )
    
    # Primes taxables (calculées automatiquement)
    prime_cherte_vie = forms.DecimalField(
        label="Prime de cherté de vie - Calculée automatiquement",
        min_value=0,
        decimal_places=2,
        max_digits=12,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': True, 'style': 'background-color: #f8f9fa;'})
    )
    
    
    indemnite_logement = forms.DecimalField(
        label="Indemnité de logement - Calculée automatiquement",
        min_value=0,
        decimal_places=2,
        max_digits=12,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': True, 'style': 'background-color: #f8f9fa;'})
    )
    
    indemnite_transport = forms.DecimalField(
        label="Indemnité de transport - Calculée automatiquement",
        min_value=0,
        decimal_places=2,
        max_digits=12,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': True, 'style': 'background-color: #f8f9fa;'})
    )
    
    indemnite_repas = forms.DecimalField(
        label="Indemnité de repas/panier - Calculée automatiquement",
        min_value=0,
        decimal_places=2,
        max_digits=12,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': True, 'style': 'background-color: #f8f9fa;'})
    )
    
    # Prime de responsabilité (exonérée) - activable par case à cocher
    prime_responsabilite_exoneree = forms.BooleanField(
        label="Prime de responsabilité",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input exempt-prime', 'disabled': True})
    )
    
    # Avantage en nature
    avantage_nature = forms.DecimalField(
        label="Avantage en nature",
        min_value=0,
        decimal_places=2,
        max_digits=12,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': "Entrez l'avantage en nature (si applicable)"})
    )
    
    
    # Déductions pour le salaire net à payer
    avance_salaire = forms.DecimalField(
        label="Avance sur salaire",
        min_value=0,
        decimal_places=2,
        max_digits=12,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    saisie_opposition = forms.DecimalField(
        label="Saisie et opposition",
        min_value=0,
        decimal_places=2,
        max_digits=12,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Calculer le total des primes taxables
        # Gérer les valeurs None en les convertissant en 0
        prime_cherte_vie = cleaned_data.get('prime_cherte_vie') or 0
        indemnite_logement = cleaned_data.get('indemnite_logement') or 0
        indemnite_transport = cleaned_data.get('indemnite_transport') or 0
        indemnite_repas = cleaned_data.get('indemnite_repas') or 0
        
        primes_taxables = (
            prime_cherte_vie +
            indemnite_logement +
            indemnite_transport +
            indemnite_repas
        )
        
        # Calculer le total des primes exonérées
        prime_retraite = cleaned_data.get('prime_retraite') or 0
        prime_interim = cleaned_data.get('prime_interim') or 0
        prime_anciennete = cleaned_data.get('prime_anciennete') or 0
        
        primes_exonerees = (
            prime_retraite +
            prime_interim +
            prime_anciennete
        )
        
        # Calculer le salaire net à payer
        avance_salaire = cleaned_data.get('avance_salaire') or 0
        saisie_opposition = cleaned_data.get('saisie_opposition') or 0
        salaire_net = cleaned_data.get('net_salary') or 0  # Corriger le nom du champ
        
        # S'assurer que les valeurs sont des nombres
        try:
            avance_salaire = float(avance_salaire) if avance_salaire else 0
            saisie_opposition = float(saisie_opposition) if saisie_opposition else 0
            salaire_net = float(salaire_net) if salaire_net else 0
        except (ValueError, TypeError):
            avance_salaire = 0
            saisie_opposition = 0
            salaire_net = 0
        
        salaire_net_a_payer = salaire_net - (avance_salaire + saisie_opposition)
        
        cleaned_data['primes_taxables'] = primes_taxables
        cleaned_data['primes_exonerees'] = primes_exonerees
        cleaned_data['salaire_net_a_payer'] = salaire_net_a_payer
        return cleaned_data
