"""
Moroccan Chart of Accounts (Plan Comptable Marocain - PCM)
This module provides the structure and data for the Moroccan Chart of Accounts.
"""

from app import db
from models import Account

def initialize_pcm():
    """
    Initialize the Moroccan Chart of Accounts in the database.
    Creates all standard accounts defined in the PCM if they don't already exist.
    """
    # Only initialize if there are no accounts in the database
    if Account.query.count() == 0:
        # Create accounts by class
        create_class_1_accounts()
        create_class_2_accounts()
        create_class_3_accounts()
        create_class_4_accounts()
        create_class_5_accounts()
        create_class_6_accounts()
        create_class_7_accounts()
        
        # Commit all changes
        db.session.commit()
        
        return True
    
    return False

def create_class_1_accounts():
    """Create Class 1 accounts: Financing Accounts"""
    # Main parent accounts
    class_1 = Account(
        code="1", 
        name="Comptes de financement permanent",
        account_class=1,
        account_type="Equity"
    )
    db.session.add(class_1)
    db.session.flush()
    
    # Subgroup accounts
    accounts = [
        Account(
            code="11", 
            name="Capitaux propres",
            account_class=1,
            account_type="Equity",
            parent_id=class_1.id
        ),
        Account(
            code="13", 
            name="Capitaux propres assimilés",
            account_class=1,
            account_type="Equity",
            parent_id=class_1.id
        ),
        Account(
            code="14", 
            name="Dettes de financement",
            account_class=1,
            account_type="Liability",
            parent_id=class_1.id
        ),
        Account(
            code="15", 
            name="Provisions durables pour risques et charges",
            account_class=1,
            account_type="Liability",
            parent_id=class_1.id
        ),
        Account(
            code="16", 
            name="Comptes de liaison des établissements et succursales",
            account_class=1,
            account_type="Equity",
            parent_id=class_1.id
        ),
        Account(
            code="17", 
            name="Écarts de conversion - Passif",
            account_class=1,
            account_type="Equity",
            parent_id=class_1.id
        ),
        Account(
            code="18", 
            name="Comptes de liaison des sociétés en participation",
            account_class=1,
            account_type="Equity",
            parent_id=class_1.id
        ),
    ]
    
    for account in accounts:
        db.session.add(account)
    
    db.session.flush()
    
    # Detailed accounts for each subgroup
    # Capital and reserves (11)
    capital_account = next(a for a in accounts if a.code == "11")
    capital_accounts = [
        Account(
            code="111", 
            name="Capital social ou personnel",
            account_class=1,
            account_type="Equity",
            parent_id=capital_account.id
        ),
        Account(
            code="112", 
            name="Primes d'émission, de fusion et d'apport",
            account_class=1,
            account_type="Equity",
            parent_id=capital_account.id
        ),
        Account(
            code="113", 
            name="Écarts de réévaluation",
            account_class=1,
            account_type="Equity",
            parent_id=capital_account.id
        ),
        Account(
            code="114", 
            name="Réserve légale",
            account_class=1,
            account_type="Equity",
            parent_id=capital_account.id
        ),
        Account(
            code="115", 
            name="Autres réserves",
            account_class=1,
            account_type="Equity",
            parent_id=capital_account.id
        ),
        Account(
            code="116", 
            name="Report à nouveau",
            account_class=1,
            account_type="Equity",
            parent_id=capital_account.id
        ),
        Account(
            code="118", 
            name="Résultats nets en instance d'affectation",
            account_class=1,
            account_type="Equity",
            parent_id=capital_account.id
        ),
        Account(
            code="119", 
            name="Résultat net de l'exercice",
            account_class=1,
            account_type="Equity",
            parent_id=capital_account.id
        ),
    ]
    
    for account in capital_accounts:
        db.session.add(account)
    
    # Similar structure for other subgroups...
    # Long-term financing (14)
    financing_account = next(a for a in accounts if a.code == "14")
    financing_accounts = [
        Account(
            code="141", 
            name="Emprunts obligataires",
            account_class=1,
            account_type="Liability",
            parent_id=financing_account.id
        ),
        Account(
            code="148", 
            name="Autres dettes de financement",
            account_class=1,
            account_type="Liability",
            parent_id=financing_account.id
        ),
    ]
    
    for account in financing_accounts:
        db.session.add(account)

def create_class_2_accounts():
    """Create Class 2 accounts: Fixed Assets"""
    # Main parent account
    class_2 = Account(
        code="2", 
        name="Comptes d'actif immobilisé",
        account_class=2,
        account_type="Asset"
    )
    db.session.add(class_2)
    db.session.flush()
    
    # Subgroup accounts
    accounts = [
        Account(
            code="21", 
            name="Immobilisations en non-valeurs",
            account_class=2,
            account_type="Asset",
            parent_id=class_2.id
        ),
        Account(
            code="22", 
            name="Immobilisations incorporelles",
            account_class=2,
            account_type="Asset",
            parent_id=class_2.id
        ),
        Account(
            code="23", 
            name="Immobilisations corporelles",
            account_class=2,
            account_type="Asset",
            parent_id=class_2.id
        ),
        Account(
            code="24", 
            name="Immobilisations financières",
            account_class=2,
            account_type="Asset",
            parent_id=class_2.id
        ),
        Account(
            code="25", 
            name="Immobilisations en cours",
            account_class=2,
            account_type="Asset",
            parent_id=class_2.id
        ),
        Account(
            code="27", 
            name="Écarts de conversion - Actif",
            account_class=2,
            account_type="Asset",
            parent_id=class_2.id
        ),
        Account(
            code="28", 
            name="Amortissements des immobilisations",
            account_class=2,
            account_type="Asset",
            parent_id=class_2.id
        ),
        Account(
            code="29", 
            name="Provisions pour dépréciation des immobilisations",
            account_class=2,
            account_type="Asset",
            parent_id=class_2.id
        ),
    ]
    
    for account in accounts:
        db.session.add(account)
    
    db.session.flush()
    
    # Detailed accounts for some subgroups
    # Intangible assets (22)
    intangible_account = next(a for a in accounts if a.code == "22")
    intangible_accounts = [
        Account(
            code="221", 
            name="Immobilisations en recherche et développement",
            account_class=2,
            account_type="Asset",
            parent_id=intangible_account.id
        ),
        Account(
            code="222", 
            name="Brevets, marques, droits et valeurs similaires",
            account_class=2,
            account_type="Asset",
            parent_id=intangible_account.id
        ),
        Account(
            code="223", 
            name="Fonds commercial",
            account_class=2,
            account_type="Asset",
            parent_id=intangible_account.id
        ),
    ]
    
    for account in intangible_accounts:
        db.session.add(account)
    
    # Tangible assets (23)
    tangible_account = next(a for a in accounts if a.code == "23")
    tangible_accounts = [
        Account(
            code="231", 
            name="Terrains",
            account_class=2,
            account_type="Asset",
            parent_id=tangible_account.id
        ),
        Account(
            code="232", 
            name="Constructions",
            account_class=2,
            account_type="Asset",
            parent_id=tangible_account.id
        ),
        Account(
            code="233", 
            name="Installations techniques, matériel et outillage",
            account_class=2,
            account_type="Asset",
            parent_id=tangible_account.id
        ),
        Account(
            code="234", 
            name="Matériel de transport",
            account_class=2,
            account_type="Asset",
            parent_id=tangible_account.id
        ),
        Account(
            code="235", 
            name="Mobilier, matériel de bureau et aménagements divers",
            account_class=2,
            account_type="Asset",
            parent_id=tangible_account.id
        ),
    ]
    
    for account in tangible_accounts:
        db.session.add(account)

def create_class_3_accounts():
    """Create Class 3 accounts: Current Assets"""
    # Main parent account
    class_3 = Account(
        code="3", 
        name="Comptes d'actif circulant (hors trésorerie)",
        account_class=3,
        account_type="Asset"
    )
    db.session.add(class_3)
    db.session.flush()
    
    # Subgroup accounts
    accounts = [
        Account(
            code="31", 
            name="Stocks",
            account_class=3,
            account_type="Asset",
            parent_id=class_3.id
        ),
        Account(
            code="34", 
            name="Créances de l'actif circulant",
            account_class=3,
            account_type="Asset",
            parent_id=class_3.id
        ),
        Account(
            code="35", 
            name="Titres et valeurs de placement",
            account_class=3,
            account_type="Asset",
            parent_id=class_3.id
        ),
        Account(
            code="37", 
            name="Écarts de conversion - Actif (Éléments circulants)",
            account_class=3,
            account_type="Asset",
            parent_id=class_3.id
        ),
        Account(
            code="39", 
            name="Provisions pour dépréciation des comptes de l'actif circulant",
            account_class=3,
            account_type="Asset",
            parent_id=class_3.id
        ),
    ]
    
    for account in accounts:
        db.session.add(account)
    
    db.session.flush()
    
    # Detailed accounts for some subgroups
    # Stocks (31)
    stocks_account = next(a for a in accounts if a.code == "31")
    stocks_accounts = [
        Account(
            code="311", 
            name="Marchandises",
            account_class=3,
            account_type="Asset",
            parent_id=stocks_account.id
        ),
        Account(
            code="312", 
            name="Matières et fournitures consommables",
            account_class=3,
            account_type="Asset",
            parent_id=stocks_account.id
        ),
        Account(
            code="313", 
            name="Produits en cours",
            account_class=3,
            account_type="Asset",
            parent_id=stocks_account.id
        ),
        Account(
            code="314", 
            name="Produits intermédiaires et produits résiduels",
            account_class=3,
            account_type="Asset",
            parent_id=stocks_account.id
        ),
        Account(
            code="315", 
            name="Produits finis",
            account_class=3,
            account_type="Asset",
            parent_id=stocks_account.id
        ),
    ]
    
    for account in stocks_accounts:
        db.session.add(account)
    
    # Receivables (34)
    receivables_account = next(a for a in accounts if a.code == "34")
    receivables_accounts = [
        Account(
            code="341", 
            name="Fournisseurs débiteurs, avances et acomptes",
            account_class=3,
            account_type="Asset",
            parent_id=receivables_account.id
        ),
        Account(
            code="342", 
            name="Clients et comptes rattachés",
            account_class=3,
            account_type="Asset",
            parent_id=receivables_account.id
        ),
        Account(
            code="343", 
            name="Personnel - débiteur",
            account_class=3,
            account_type="Asset",
            parent_id=receivables_account.id
        ),
        Account(
            code="345", 
            name="État - débiteur",
            account_class=3,
            account_type="Asset",
            parent_id=receivables_account.id
        ),
        Account(
            code="346", 
            name="Comptes d'associés - débiteurs",
            account_class=3,
            account_type="Asset",
            parent_id=receivables_account.id
        ),
        Account(
            code="348", 
            name="Autres débiteurs",
            account_class=3,
            account_type="Asset",
            parent_id=receivables_account.id
        ),
        Account(
            code="349", 
            name="Comptes de régularisation - actif",
            account_class=3,
            account_type="Asset",
            parent_id=receivables_account.id
        ),
    ]
    
    for account in receivables_accounts:
        db.session.add(account)
    
    # State receivables (345)
    state_receivables = next(a for a in receivables_accounts if a.code == "345")
    state_receivables_accounts = [
        Account(
            code="3451", 
            name="Subventions à recevoir",
            account_class=3,
            account_type="Asset",
            parent_id=state_receivables.id
        ),
        Account(
            code="3455", 
            name="État - TVA récupérable",
            account_class=3,
            account_type="Asset",
            parent_id=state_receivables.id
        ),
        Account(
            code="3456", 
            name="État - Crédit de TVA (suivant déclaration)",
            account_class=3,
            account_type="Asset",
            parent_id=state_receivables.id
        ),
        Account(
            code="3458", 
            name="État - Autres comptes débiteurs",
            account_class=3,
            account_type="Asset",
            parent_id=state_receivables.id
        ),
    ]
    
    for account in state_receivables_accounts:
        db.session.add(account)

def create_class_4_accounts():
    """Create Class 4 accounts: Current Liabilities"""
    # Main parent account
    class_4 = Account(
        code="4", 
        name="Comptes de passif circulant (hors trésorerie)",
        account_class=4,
        account_type="Liability"
    )
    db.session.add(class_4)
    db.session.flush()
    
    # Subgroup accounts
    accounts = [
        Account(
            code="44", 
            name="Dettes du passif circulant",
            account_class=4,
            account_type="Liability",
            parent_id=class_4.id
        ),
        Account(
            code="45", 
            name="Autres provisions pour risques et charges",
            account_class=4,
            account_type="Liability",
            parent_id=class_4.id
        ),
        Account(
            code="47", 
            name="Écarts de conversion - Passif (Éléments circulants)",
            account_class=4,
            account_type="Liability",
            parent_id=class_4.id
        ),
    ]
    
    for account in accounts:
        db.session.add(account)
    
    db.session.flush()
    
    # Detailed accounts for some subgroups
    # Payables (44)
    payables_account = next(a for a in accounts if a.code == "44")
    payables_accounts = [
        Account(
            code="441", 
            name="Fournisseurs et comptes rattachés",
            account_class=4,
            account_type="Liability",
            parent_id=payables_account.id
        ),
        Account(
            code="442", 
            name="Clients créditeurs, avances et acomptes",
            account_class=4,
            account_type="Liability",
            parent_id=payables_account.id
        ),
        Account(
            code="443", 
            name="Personnel - créditeur",
            account_class=4,
            account_type="Liability",
            parent_id=payables_account.id
        ),
        Account(
            code="444", 
            name="Organismes sociaux",
            account_class=4,
            account_type="Liability",
            parent_id=payables_account.id
        ),
        Account(
            code="445", 
            name="État - créditeur",
            account_class=4,
            account_type="Liability",
            parent_id=payables_account.id
        ),
        Account(
            code="446", 
            name="Comptes d'associés - créditeurs",
            account_class=4,
            account_type="Liability",
            parent_id=payables_account.id
        ),
        Account(
            code="448", 
            name="Autres créanciers",
            account_class=4,
            account_type="Liability",
            parent_id=payables_account.id
        ),
        Account(
            code="449", 
            name="Comptes de régularisation - passif",
            account_class=4,
            account_type="Liability",
            parent_id=payables_account.id
        ),
    ]
    
    for account in payables_accounts:
        db.session.add(account)
    
    # State payables (445)
    state_payables = next(a for a in payables_accounts if a.code == "445")
    state_payables_accounts = [
        Account(
            code="4451", 
            name="État - TVA facturée",
            account_class=4,
            account_type="Liability",
            parent_id=state_payables.id
        ),
        Account(
            code="4452", 
            name="État - TVA due (suivant déclaration)",
            account_class=4,
            account_type="Liability",
            parent_id=state_payables.id
        ),
        Account(
            code="4453", 
            name="État - Acomptes sur impôts sur les résultats",
            account_class=4,
            account_type="Liability",
            parent_id=state_payables.id
        ),
        Account(
            code="4454", 
            name="État - Impôts sur les résultats",
            account_class=4,
            account_type="Liability",
            parent_id=state_payables.id
        ),
        Account(
            code="4455", 
            name="État - Taxes sur le chiffre d'affaires",
            account_class=4,
            account_type="Liability",
            parent_id=state_payables.id
        ),
        Account(
            code="4456", 
            name="État - Taxes sur le revenu",
            account_class=4,
            account_type="Liability",
            parent_id=state_payables.id
        ),
        Account(
            code="4458", 
            name="État - Autres comptes créditeurs",
            account_class=4,
            account_type="Liability",
            parent_id=state_payables.id
        ),
    ]
    
    for account in state_payables_accounts:
        db.session.add(account)

def create_class_5_accounts():
    """Create Class 5 accounts: Cash and Cash Equivalents"""
    # Main parent account
    class_5 = Account(
        code="5", 
        name="Comptes de trésorerie",
        account_class=5,
        account_type="Asset"
    )
    db.session.add(class_5)
    db.session.flush()
    
    # Subgroup accounts
    accounts = [
        Account(
            code="51", 
            name="Trésorerie - Actif",
            account_class=5,
            account_type="Asset",
            parent_id=class_5.id
        ),
        Account(
            code="55", 
            name="Trésorerie - Passif",
            account_class=5,
            account_type="Liability",
            parent_id=class_5.id
        ),
        Account(
            code="59", 
            name="Provisions pour dépréciation des comptes de trésorerie",
            account_class=5,
            account_type="Asset",
            parent_id=class_5.id
        ),
    ]
    
    for account in accounts:
        db.session.add(account)
    
    db.session.flush()
    
    # Detailed accounts for some subgroups
    # Cash - Asset (51)
    cash_asset_account = next(a for a in accounts if a.code == "51")
    cash_asset_accounts = [
        Account(
            code="511", 
            name="Chèques et valeurs à encaisser",
            account_class=5,
            account_type="Asset",
            parent_id=cash_asset_account.id
        ),
        Account(
            code="512", 
            name="Banques, Trésorerie Générale et CCP",
            account_class=5,
            account_type="Asset",
            parent_id=cash_asset_account.id
        ),
        Account(
            code="514", 
            name="Régies d'avances et accréditifs",
            account_class=5,
            account_type="Asset",
            parent_id=cash_asset_account.id
        ),
        Account(
            code="516", 
            name="Caisses, régies d'avances et accréditifs",
            account_class=5,
            account_type="Asset",
            parent_id=cash_asset_account.id
        ),
    ]
    
    for account in cash_asset_accounts:
        db.session.add(account)
    
    # Cash - Liability (55)
    cash_liability_account = next(a for a in accounts if a.code == "55")
    cash_liability_accounts = [
        Account(
            code="552", 
            name="Crédits d'escompte",
            account_class=5,
            account_type="Liability",
            parent_id=cash_liability_account.id
        ),
        Account(
            code="553", 
            name="Crédits de trésorerie",
            account_class=5,
            account_type="Liability",
            parent_id=cash_liability_account.id
        ),
        Account(
            code="554", 
            name="Banques (soldes créditeurs)",
            account_class=5,
            account_type="Liability",
            parent_id=cash_liability_account.id
        ),
    ]
    
    for account in cash_liability_accounts:
        db.session.add(account)

def create_class_6_accounts():
    """Create Class 6 accounts: Expenses"""
    # Main parent account
    class_6 = Account(
        code="6", 
        name="Comptes de charges",
        account_class=6,
        account_type="Expense"
    )
    db.session.add(class_6)
    db.session.flush()
    
    # Subgroup accounts
    accounts = [
        Account(
            code="61", 
            name="Charges d'exploitation",
            account_class=6,
            account_type="Expense",
            parent_id=class_6.id
        ),
        Account(
            code="63", 
            name="Charges d'exploitation - Impôts et taxes",
            account_class=6,
            account_type="Expense",
            parent_id=class_6.id
        ),
        Account(
            code="64", 
            name="Charges de personnel",
            account_class=6,
            account_type="Expense",
            parent_id=class_6.id
        ),
        Account(
            code="65", 
            name="Autres charges d'exploitation",
            account_class=6,
            account_type="Expense",
            parent_id=class_6.id
        ),
        Account(
            code="66", 
            name="Charges financières",
            account_class=6,
            account_type="Expense",
            parent_id=class_6.id
        ),
        Account(
            code="67", 
            name="Charges non courantes",
            account_class=6,
            account_type="Expense",
            parent_id=class_6.id
        ),
        Account(
            code="68", 
            name="Dotations d'exploitation",
            account_class=6,
            account_type="Expense",
            parent_id=class_6.id
        ),
        Account(
            code="69", 
            name="Impôts sur les résultats",
            account_class=6,
            account_type="Expense",
            parent_id=class_6.id
        ),
    ]
    
    for account in accounts:
        db.session.add(account)
    
    db.session.flush()
    
    # Detailed accounts for some subgroups
    # Operating expenses (61)
    operating_expense_account = next(a for a in accounts if a.code == "61")
    operating_expense_accounts = [
        Account(
            code="611", 
            name="Achats revendus de marchandises",
            account_class=6,
            account_type="Expense",
            parent_id=operating_expense_account.id
        ),
        Account(
            code="612", 
            name="Achats consommés de matières et fournitures",
            account_class=6,
            account_type="Expense",
            parent_id=operating_expense_account.id
        ),
        Account(
            code="613", 
            name="Autres charges externes",
            account_class=6,
            account_type="Expense",
            parent_id=operating_expense_account.id
        ),
        Account(
            code="614", 
            name="Charges de personnel",
            account_class=6,
            account_type="Expense",
            parent_id=operating_expense_account.id
        ),
    ]
    
    for account in operating_expense_accounts:
        db.session.add(account)
    
    # External expenses (613)
    external_expense = next(a for a in operating_expense_accounts if a.code == "613")
    external_expense_accounts = [
        Account(
            code="6131", 
            name="Locations et charges locatives",
            account_class=6,
            account_type="Expense",
            parent_id=external_expense.id
        ),
        Account(
            code="6132", 
            name="Redevances de crédit-bail",
            account_class=6,
            account_type="Expense",
            parent_id=external_expense.id
        ),
        Account(
            code="6133", 
            name="Entretien et réparations",
            account_class=6,
            account_type="Expense",
            parent_id=external_expense.id
        ),
        Account(
            code="6134", 
            name="Primes d'assurances",
            account_class=6,
            account_type="Expense",
            parent_id=external_expense.id
        ),
        Account(
            code="6135", 
            name="Rémunérations du personnel extérieur à l'entreprise",
            account_class=6,
            account_type="Expense",
            parent_id=external_expense.id
        ),
        Account(
            code="6136", 
            name="Rémunérations d'intermédiaires et honoraires",
            account_class=6,
            account_type="Expense",
            parent_id=external_expense.id
        ),
        Account(
            code="6137", 
            name="Redevances pour brevets, marques, droits...",
            account_class=6,
            account_type="Expense",
            parent_id=external_expense.id
        ),
        Account(
            code="6141", 
            name="Études, recherches et documentation",
            account_class=6,
            account_type="Expense",
            parent_id=external_expense.id
        ),
        Account(
            code="6142", 
            name="Transports",
            account_class=6,
            account_type="Expense",
            parent_id=external_expense.id
        ),
        Account(
            code="6143", 
            name="Déplacements, missions et réceptions",
            account_class=6,
            account_type="Expense",
            parent_id=external_expense.id
        ),
        Account(
            code="6144", 
            name="Publicité, publications et relations publiques",
            account_class=6,
            account_type="Expense",
            parent_id=external_expense.id
        ),
        Account(
            code="6145", 
            name="Frais postaux et frais de télécommunications",
            account_class=6,
            account_type="Expense",
            parent_id=external_expense.id
        ),
        Account(
            code="6146", 
            name="Cotisations et dons",
            account_class=6,
            account_type="Expense",
            parent_id=external_expense.id
        ),
        Account(
            code="6147", 
            name="Services bancaires",
            account_class=6,
            account_type="Expense",
            parent_id=external_expense.id
        ),
        Account(
            code="6148", 
            name="Autres charges externes des exercices antérieurs",
            account_class=6,
            account_type="Expense",
            parent_id=external_expense.id
        ),
    ]
    
    for account in external_expense_accounts:
        db.session.add(account)
    
    # Personnel expenses (64)
    personnel_expense_account = next(a for a in accounts if a.code == "64")
    personnel_expense_accounts = [
        Account(
            code="641", 
            name="Rémunérations du personnel",
            account_class=6,
            account_type="Expense",
            parent_id=personnel_expense_account.id
        ),
        Account(
            code="643", 
            name="Rémunérations des administrateurs, gérants et associés",
            account_class=6,
            account_type="Expense",
            parent_id=personnel_expense_account.id
        ),
        Account(
            code="644", 
            name="Charges sociales",
            account_class=6,
            account_type="Expense",
            parent_id=personnel_expense_account.id
        ),
        Account(
            code="646", 
            name="Charges sociales diverses",
            account_class=6,
            account_type="Expense",
            parent_id=personnel_expense_account.id
        ),
    ]
    
    for account in personnel_expense_accounts:
        db.session.add(account)

def create_class_7_accounts():
    """Create Class 7 accounts: Revenues"""
    # Main parent account
    class_7 = Account(
        code="7", 
        name="Comptes de produits",
        account_class=7,
        account_type="Revenue"
    )
    db.session.add(class_7)
    db.session.flush()
    
    # Subgroup accounts
    accounts = [
        Account(
            code="71", 
            name="Produits d'exploitation",
            account_class=7,
            account_type="Revenue",
            parent_id=class_7.id
        ),
        Account(
            code="73", 
            name="Produits d'exploitation - Variations de stocks",
            account_class=7,
            account_type="Revenue",
            parent_id=class_7.id
        ),
        Account(
            code="75", 
            name="Autres produits d'exploitation",
            account_class=7,
            account_type="Revenue",
            parent_id=class_7.id
        ),
        Account(
            code="76", 
            name="Produits financiers",
            account_class=7,
            account_type="Revenue",
            parent_id=class_7.id
        ),
        Account(
            code="77", 
            name="Produits non courants",
            account_class=7,
            account_type="Revenue",
            parent_id=class_7.id
        ),
        Account(
            code="78", 
            name="Reprises d'exploitation",
            account_class=7,
            account_type="Revenue",
            parent_id=class_7.id
        ),
        Account(
            code="79", 
            name="Reprises non courantes",
            account_class=7,
            account_type="Revenue",
            parent_id=class_7.id
        ),
    ]
    
    for account in accounts:
        db.session.add(account)
    
    db.session.flush()
    
    # Detailed accounts for some subgroups
    # Operating revenues (71)
    operating_revenue_account = next(a for a in accounts if a.code == "71")
    operating_revenue_accounts = [
        Account(
            code="711", 
            name="Ventes de marchandises",
            account_class=7,
            account_type="Revenue",
            parent_id=operating_revenue_account.id
        ),
        Account(
            code="712", 
            name="Ventes de biens et services produits",
            account_class=7,
            account_type="Revenue",
            parent_id=operating_revenue_account.id
        ),
    ]
    
    for account in operating_revenue_accounts:
        db.session.add(account)
    
    # Sales of goods and services (712)
    sales_account = next(a for a in operating_revenue_accounts if a.code == "712")
    sales_accounts = [
        Account(
            code="7121", 
            name="Ventes de biens produits au Maroc",
            account_class=7,
            account_type="Revenue",
            parent_id=sales_account.id
        ),
        Account(
            code="7122", 
            name="Ventes de biens produits à l'étranger",
            account_class=7,
            account_type="Revenue",
            parent_id=sales_account.id
        ),
        Account(
            code="7124", 
            name="Ventes de services produits au Maroc",
            account_class=7,
            account_type="Revenue",
            parent_id=sales_account.id
        ),
        Account(
            code="7125", 
            name="Ventes de services produits à l'étranger",
            account_class=7,
            account_type="Revenue",
            parent_id=sales_account.id
        ),
        Account(
            code="7128", 
            name="Autres ventes de biens et services produits",
            account_class=7,
            account_type="Revenue",
            parent_id=sales_account.id
        ),
    ]
    
    for account in sales_accounts:
        db.session.add(account)
    
    # Financial revenues (76)
    financial_revenue_account = next(a for a in accounts if a.code == "76")
    financial_revenue_accounts = [
        Account(
            code="761", 
            name="Produits des titres de participation et autres titres immobilisés",
            account_class=7,
            account_type="Revenue",
            parent_id=financial_revenue_account.id
        ),
        Account(
            code="762", 
            name="Produits des autres immobilisations financières",
            account_class=7,
            account_type="Revenue",
            parent_id=financial_revenue_account.id
        ),
        Account(
            code="763", 
            name="Revenus des autres créances",
            account_class=7,
            account_type="Revenue",
            parent_id=financial_revenue_account.id
        ),
        Account(
            code="764", 
            name="Produits nets sur cessions de titres et valeurs de placement",
            account_class=7,
            account_type="Revenue",
            parent_id=financial_revenue_account.id
        ),
        Account(
            code="765", 
            name="Intérêts et produits assimilés",
            account_class=7,
            account_type="Revenue",
            parent_id=financial_revenue_account.id
        ),
        Account(
            code="766", 
            name="Gains de change",
            account_class=7,
            account_type="Revenue",
            parent_id=financial_revenue_account.id
        ),
        Account(
            code="768", 
            name="Autres produits financiers",
            account_class=7,
            account_type="Revenue",
            parent_id=financial_revenue_account.id
        ),
    ]
    
    for account in financial_revenue_accounts:
        db.session.add(account)
