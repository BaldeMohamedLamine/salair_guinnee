# =============================
# 1️⃣ FONCTIONS DE BASE (CNSS + RTS)
# =============================

def calculate_exempt_primes_amounts(net_salary, selected_primes):
    """
    Calcule automatiquement les montants des primes exonérées
    basé sur le salaire net et les primes sélectionnées.
    
    Args:
        net_salary: Salaire net souhaité
        selected_primes: Liste des primes sélectionnées ['retraite', 'interim', 'anciennete']
    
    Returns:
        dict: Montants calculés pour chaque prime
    """
    from decimal import Decimal
    
    amounts = {
        'prime_retraite': 0,
        'prime_interim': 0,
        'prime_anciennete': 0
    }
    
    if not selected_primes:
        return amounts
    
    # Convertir net_salary en Decimal si ce n'est pas déjà le cas
    net_salary = Decimal(str(net_salary))
    
    # Calculer un montant de base basé sur le salaire net
    # Utiliser 5% du salaire net comme base pour les primes exonérées
    base_amount = net_salary * Decimal('0.05')
    
    # Répartir le montant entre les primes sélectionnées
    num_selected = len(selected_primes)
    if num_selected == 0:
        return amounts
    
    amount_per_prime = base_amount / Decimal(str(num_selected))
    
    # Appliquer des coefficients spécifiques pour chaque type de prime
    coefficients = {
        'retraite': Decimal('1.2'),    # Prime de retraite légèrement plus élevée
        'interim': Decimal('0.8'),     # Prime d'intérim plus faible
        'anciennete': Decimal('1.0')   # Prime d'ancienneté standard
    }
    
    for prime in selected_primes:
        if prime == 'retraite':
            amounts['prime_retraite'] = float(amount_per_prime * coefficients['retraite'])
        elif prime == 'interim':
            amounts['prime_interim'] = float(amount_per_prime * coefficients['interim'])
        elif prime == 'anciennete':
            amounts['prime_anciennete'] = float(amount_per_prime * coefficients['anciennete'])
    
    return amounts

def calculate_cnss_employee(gross):
    """
    Calcule la CNSS employé :
    - 5% du salaire brut
    - Avec un minimum (plancher) et un maximum (plafond)
    """
    plancher = 27000
    plafond = 125000
    montant = gross * 0.05

    if montant < plancher:
        return plancher
    elif montant > plafond:
        return plafond
    return montant


def calculate_cnss_employer(gross):
    """
    Calcule la CNSS employeur :
    - 18% du salaire brut
    - Avec le même plancher et plafond que l'employé
    """
    plancher = 97200
    plafond = 450000
    montant = gross * 0.18

    if montant < plancher:
        return plancher
    elif montant > plafond:
        return plafond
    return montant


def calculate_versement_forfaitaire(gross):
    """
    Calcule le versement forfaitaire :
    - 6% du salaire brut
    """
    return gross * 0.06


def calculate_taxe_apprentissage(gross):
    """
    Calcule la taxe d'apprentissage :
    - 2% du salaire brut
    """
    return gross * 0.02


def calculate_rts(imposable):
    """
    Calcule la RTS en fonction du revenu imposable.
    Barème progressif :
    - 0% jusqu 1.000.000
    - 5% entre 1.000.001 et 3.000.000
    - 8% entre 3.000.001 et 5.000.000
    - 10% entre 5.000.001 et 10.000.000
    - 15% entre 10.000.001 et 20.000.000
    - 20% au-delà de 20.000.000
    """
    if imposable <= 1_000_000:
        return 0
    elif imposable <= 3_000_000:
        return (imposable - 1_000_000) * 0.05
    elif imposable <= 5_000_000:
        return 100_000 + (imposable - 3_000_000) * 0.08
    elif imposable <= 10_000_000:
        return 260_000 + (imposable - 5_000_000) * 0.10
    elif imposable <= 20_000_000:
        return 760_000 + (imposable - 10_000_000) * 0.15
    else:
        return 2_260_000 + (imposable - 20_000_000) * 0.20


def calculate_rts_detailed(imposable):
    """
    Calcule la RTS avec le détail du calcul étape par étape.
    Affiche seulement les tranches qui s'appliquent au salaire imposable.
    Retourne (total_rts, details)
    """
    from decimal import Decimal
    
    details = []
    total_rts = Decimal('0')
    imposable = Decimal(str(imposable))
    
    # Si le salaire est inférieur ou égal à 1,000,000 GNF
    if imposable <= 1_000_000:
        details.append(f"0% jusqu'à 1,000,000 GNF = 0 GNF")
        details.append(f"Votre salaire imposable : {imposable:,.0f} GNF")
        details.append(f"RTS = 0 GNF (sous le seuil d'imposition)")
        return 0, details
    
    # Tranche 1: 0% jusqu'à 1,000,000 (toujours affichée)
    details.append(f"0% jusqu'à 1,000,000 GNF = 0 GNF")
    
    # Tranche 2: 5% de 1,000,001 à 3,000,000
    if imposable > 1_000_000:
        tranche2_max = min(imposable, 3_000_000)
        tranche2_montant = (tranche2_max - 1_000_000) * Decimal('0.05')
        total_rts += tranche2_montant
        if imposable <= 3_000_000:
            details.append(f"5% de 1,000,001 à {imposable:,.0f} GNF = {tranche2_montant:,.0f} GNF")
        else:
            details.append(f"5% de 1,000,001 à 3,000,000 GNF = {tranche2_montant:,.0f} GNF")
    
    # Tranche 3: 8% de 3,000,001 à 5,000,000
    if imposable > 3_000_000:
        tranche3_max = min(imposable, 5_000_000)
        tranche3_montant = (tranche3_max - 3_000_000) * Decimal('0.08')
        total_rts += tranche3_montant
        if imposable <= 5_000_000:
            details.append(f"8% de 3,000,001 à {imposable:,.0f} GNF = {tranche3_montant:,.0f} GNF")
        else:
            details.append(f"8% de 3,000,001 à 5,000,000 GNF = {tranche3_montant:,.0f} GNF")
    
    # Tranche 4: 10% de 5,000,001 à 10,000,000
    if imposable > 5_000_000:
        tranche4_max = min(imposable, 10_000_000)
        tranche4_montant = (tranche4_max - 5_000_000) * Decimal('0.10')
        total_rts += tranche4_montant
        if imposable <= 10_000_000:
            details.append(f"10% de 5,000,001 à {imposable:,.0f} GNF = {tranche4_montant:,.0f} GNF")
        else:
            details.append(f"10% de 5,000,001 à 10,000,000 GNF = {tranche4_montant:,.0f} GNF")
    
    # Tranche 5: 15% de 10,000,001 à 20,000,000
    if imposable > 10_000_000:
        tranche5_max = min(imposable, 20_000_000)
        tranche5_montant = (tranche5_max - 10_000_000) * Decimal('0.15')
        total_rts += tranche5_montant
        if imposable <= 20_000_000:
            details.append(f"15% de 10,000,001 à {imposable:,.0f} GNF = {tranche5_montant:,.0f} GNF")
        else:
            details.append(f"15% de 10,000,001 à 20,000,000 GNF = {tranche5_montant:,.0f} GNF")
    
    # Tranche 6: 20% au-delà de 20,000,000
    if imposable > 20_000_000:
        tranche6_montant = (imposable - 20_000_000) * Decimal('0.20')
        total_rts += tranche6_montant
        details.append(f"20% de 20,000,001 à {imposable:,.0f} GNF = {tranche6_montant:,.0f} GNF")
    
    # Ajouter le total
    details.append(f"<strong>TOTAL RTS = {total_rts:,.0f} GNF</strong>")
    
    return total_rts, details


# =============================
# 2️⃣ ÉCART IMPOSABLE (Primes > 25%)
# =============================

def calculate_ecart_imposable(gross, primes_taxables):
    """
    Vérifie si les primes taxables dépassent 25% du salaire brut.
    Si oui, le surplus est ajouté au revenu imposable.
    """
    gross = float(gross)
    primes_taxables = float(primes_taxables) if primes_taxables else 0.0

    vingt_cinq_pourcent_brut = gross * 0.25
    difference = primes_taxables - vingt_cinq_pourcent_brut

    return max(0, difference)  # Si négatif, on prend 0


# =============================
# 3️⃣ CALCUL DU NET À PARTIR DU SALAIRE DE BASE
# =============================

def calculate_net_from_basic(basic, advantages=0, ded=0, primes_taxables=0, primes_exonerees=0):
    """
    Descend du BASIC vers le NET avec tous les calculs :
    1. Calcule le salaire brut
    2. Calcule toutes les charges (CNSS, RTS, etc.)
    3. Calcule les charges patronales
    Renvoie un dictionnaire complet avec tous les détails
    """
    basic = float(basic)
    advantages = float(advantages) if advantages else 0.0
    ded = float(ded) if ded else 0.0
    primes_taxables = float(primes_taxables) if primes_taxables else 0.0
    primes_exonerees = float(primes_exonerees) if primes_exonerees else 0.0

    # 1. Calcul du brut (salaire de base + primes taxables + primes exonérées)
    gross = basic + advantages + primes_taxables + primes_exonerees

    # 2. Calcul CNSS employé
    cnss_employee = calculate_cnss_employee(gross)

    # 3. Calcul écart imposable
    ecart_imposable = calculate_ecart_imposable(gross, primes_taxables)

    # 4. Base imposable = Brut - CNSS + Écart
    imposable = gross - cnss_employee + ecart_imposable

    # 5. Calcul RTS avec détail
    rts, rts_details = calculate_rts_detailed(imposable)
    rts = float(rts)  # Convertir Decimal en float pour la compatibilité

    # 6. Calcul Net (les primes exonérées sont déjà incluses dans le brut)
    net = gross - cnss_employee - rts - ded

    # 7. Calculs côté employeur
    cnss_employer = calculate_cnss_employer(gross)
    versement_forfaitaire = calculate_versement_forfaitaire(gross)
    taxe_apprentissage = calculate_taxe_apprentissage(gross)
    
    # 8. Totaux
    total_cnss_patronal = versement_forfaitaire + taxe_apprentissage + cnss_employer
    total_charges_employee = cnss_employee + rts

    return {
        'basic': basic,
        'gross': gross,
        'net': net,
        'cnss_employee': cnss_employee,
        'cnss_employer': cnss_employer,
        'versement_forfaitaire': versement_forfaitaire,
        'taxe_apprentissage': taxe_apprentissage,
        'total_cnss_patronal': total_cnss_patronal,
        'total_charges_employee': total_charges_employee,
        'ecart_imposable': ecart_imposable,
        'imposable': imposable,
        'rts': rts,
        'rts_details': rts_details,
        'primes_taxables': primes_taxables,
        'primes_exonerees': primes_exonerees
    }


# =============================
# 4️⃣ PRIMES ET AVANTAGES AUTOMATIQUES
# =============================

def calculate_primes_automatiques(net_salary):
    """
    Calcule les primes (logement, transport, etc.)
    en pourcentage du salaire net.
    """
    net_salary = float(net_salary)

    if net_salary <= 200000:  # Petits salaires
        prime_cherte_vie = net_salary * 0.03
        indemnite_logement = net_salary * 0.05
        indemnite_transport = net_salary * 0.03
        indemnite_repas = net_salary * 0.02

    elif net_salary <= 500000:  # Salaires moyens
        prime_cherte_vie = net_salary * 0.04
        indemnite_logement = net_salary * 0.06
        indemnite_transport = net_salary * 0.04
        indemnite_repas = net_salary * 0.03

    elif net_salary <= 1000000:  # Salaires élevés
        prime_cherte_vie = net_salary * 0.05
        indemnite_logement = net_salary * 0.08
        indemnite_transport = net_salary * 0.05
        indemnite_repas = net_salary * 0.04

    else:  # Très hauts salaires
        prime_cherte_vie = net_salary * 0.06
        indemnite_logement = net_salary * 0.10
        indemnite_transport = net_salary * 0.06
        indemnite_repas = net_salary * 0.05

    return {
        'prime_cherte_vie': round(prime_cherte_vie, 2),
        'indemnite_logement': round(indemnite_logement, 2),
        'indemnite_transport': round(indemnite_transport, 2),
        'indemnite_repas': round(indemnite_repas, 2),
    }


def calculate_avantages_et_deductions_automatiques(net_salary):
    """
    Calcule les avantages généraux et les déductions
    en pourcentage du salaire net.
    """
    net_salary = float(net_salary)

    if net_salary <= 200000:
        advantages = net_salary * 0.08
        ded = net_salary * 0.02
    elif net_salary <= 500000:
        advantages = net_salary * 0.10
        ded = net_salary * 0.02
    elif net_salary <= 1000000:
        advantages = net_salary * 0.12
        ded = net_salary * 0.02
    else:
        advantages = net_salary * 0.15
        ded = net_salary * 0.02

    return {
        'advantages': round(advantages, 2),
        'ded': round(ded, 2),
    }


# =============================
# 5️⃣ REMONTER DU NET VERS LE BASIC
# =============================

def calculate_basic_from_net(target_net, advantages=0, ded=0, primes_taxables=0, primes_exonerees=0, tolerance=1):
    """
    Retrouve le salaire de base qui permet d'obtenir un net donné.
    Utilise une recherche binaire pour être précis.
    """
    target_net = float(target_net)
    advantages = float(advantages) if advantages else 0.0
    ded = float(ded) if ded else 0.0
    primes_taxables = float(primes_taxables) if primes_taxables else 0.0
    primes_exonerees = float(primes_exonerees) if primes_exonerees else 0.0
    tolerance = float(tolerance)

    low, high = 0, 100_000_000
    basic = 0

    while low <= high:
        mid = (low + high) / 2
        result = calculate_net_from_basic(mid, advantages, ded, primes_taxables, primes_exonerees)
        net = result['net']

        if abs(net - target_net) <= tolerance:
            basic = mid
            break

        if net < target_net:
            low = mid + 1
        else:
            high = mid - 1

    # Calcul final avec tous les détails
    result = calculate_net_from_basic(basic, advantages, ded, primes_taxables, primes_exonerees)
    
    return {
        "basic": round(result['basic'], 2),
        "gross": round(result['gross'], 2),
        "net": round(result['net'], 2),
        "cnss": round(result['cnss_employee'], 2),
        "rts": round(result['rts'], 2),
        "ecart_imposable": round(result['ecart_imposable'], 2),
        "advantages": round(advantages, 2),
        "primes_taxables": round(primes_taxables, 2),
        "primes_exonerees": round(primes_exonerees, 2),
        "deductions": round(ded, 2),
        # Nouvelles données
        "cnss_employer": round(result['cnss_employer'], 2),
        "versement_forfaitaire": round(result['versement_forfaitaire'], 2),
        "taxe_apprentissage": round(result['taxe_apprentissage'], 2),
        "total_cnss_patronal": round(result['total_cnss_patronal'], 2),
        "total_charges_employee": round(result['total_charges_employee'], 2),
        "imposable": round(result['imposable'], 2),
        "rts_details": result['rts_details']
    }
