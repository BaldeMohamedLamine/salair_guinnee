from .models import Company

def company_info(request):
    """Context processor pour rendre les informations de l'entreprise disponibles partout"""
    try:
        company = Company.get_company()
        return {
            'company': company,
            'company_logo': company.logo.url if company.logo else None,
            'company_name': company.name,
        }
    except Exception:
        # En cas d'erreur, retourner des valeurs par défaut
        return {
            'company': None,
            'company_logo': None,
            'company_name': 'Mon Entreprise',
        }
