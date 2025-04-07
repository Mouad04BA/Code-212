from app import db
from models import Account, JournalEntry, JournalEntryLine
from datetime import datetime
from sqlalchemy import and_, func

def generate_balance_sheet(date):
    """
    Generate a balance sheet as of a specific date.
    
    Args:
        date (date): The date for which to generate the balance sheet
        
    Returns:
        dict: Balance sheet data
    """
    # Get all accounts
    accounts = Account.query.all()
    
    # Prepare balance sheet structure
    balance_sheet = {
        'date': date,
        'assets': {
            'non_current': [],
            'current': [],
            'cash': [],
            'total_non_current': 0,
            'total_current': 0,
            'total_cash': 0,
            'total': 0
        },
        'liabilities': {
            'equity': [],
            'non_current': [],
            'current': [],
            'total_equity': 0,
            'total_non_current': 0,
            'total_current': 0,
            'total': 0
        }
    }
    
    # Process each account
    for account in accounts:
        # Calculate account balance
        if account.account_type == 'Asset':
            # For asset accounts: Debit - Credit
            balance = db.session.query(func.sum(JournalEntryLine.debit - JournalEntryLine.credit)).\
                join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id).\
                filter(
                    JournalEntryLine.account_id == account.id,
                    JournalEntry.date <= date
                ).scalar() or 0
        else:
            # For liability and equity accounts: Credit - Debit
            balance = db.session.query(func.sum(JournalEntryLine.credit - JournalEntryLine.debit)).\
                join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id).\
                filter(
                    JournalEntryLine.account_id == account.id,
                    JournalEntry.date <= date
                ).scalar() or 0
        
        # Skip accounts with zero balance
        if balance == 0:
            continue
        
        # Add account to appropriate section of balance sheet
        account_data = {
            'code': account.code,
            'name': account.name,
            'balance': balance
        }
        
        if account.account_type == 'Asset':
            if account.account_class == 2:  # Class 2: Non-current assets
                balance_sheet['assets']['non_current'].append(account_data)
                balance_sheet['assets']['total_non_current'] += balance
            elif account.account_class == 3:  # Class 3: Current assets
                balance_sheet['assets']['current'].append(account_data)
                balance_sheet['assets']['total_current'] += balance
            elif account.account_class == 5:  # Class 5: Cash and equivalents
                balance_sheet['assets']['cash'].append(account_data)
                balance_sheet['assets']['total_cash'] += balance
            
            balance_sheet['assets']['total'] += balance
            
        elif account.account_type in ['Liability', 'Equity']:
            if account.account_class == 1:  # Class 1: Equity and long-term financing
                balance_sheet['liabilities']['equity'].append(account_data)
                balance_sheet['liabilities']['total_equity'] += balance
            elif account.account_class in [1, 2]:  # Non-current liabilities
                balance_sheet['liabilities']['non_current'].append(account_data)
                balance_sheet['liabilities']['total_non_current'] += balance
            elif account.account_class == 4:  # Class 4: Current liabilities
                balance_sheet['liabilities']['current'].append(account_data)
                balance_sheet['liabilities']['total_current'] += balance
            
            balance_sheet['liabilities']['total'] += balance
    
    # Add net income to equity
    net_income = calculate_net_income(date.replace(month=1, day=1), date)
    
    balance_sheet['liabilities']['equity'].append({
        'code': '',
        'name': 'Résultat net de la période',
        'balance': net_income
    })
    
    balance_sheet['liabilities']['total_equity'] += net_income
    balance_sheet['liabilities']['total'] += net_income
    
    return balance_sheet

def generate_income_statement(start_date, end_date):
    """
    Generate an income statement for a specific period.
    
    Args:
        start_date (date): The start date of the period
        end_date (date): The end date of the period
        
    Returns:
        dict: Income statement data
    """
    # Get relevant accounts
    revenue_accounts = Account.query.filter(Account.code.like('7%')).all()
    expense_accounts = Account.query.filter(Account.code.like('6%')).all()
    
    # Prepare income statement structure
    income_statement = {
        'start_date': start_date,
        'end_date': end_date,
        'revenues': [],
        'expenses': [],
        'total_revenue': 0,
        'total_expense': 0,
        'net_income': 0
    }
    
    # Process revenue accounts
    for account in revenue_accounts:
        # Calculate account balance: Credit - Debit
        balance = db.session.query(func.sum(JournalEntryLine.credit - JournalEntryLine.debit)).\
            join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id).\
            filter(
                JournalEntryLine.account_id == account.id,
                and_(JournalEntry.date >= start_date, JournalEntry.date <= end_date)
            ).scalar() or 0
        
        # Skip accounts with zero balance
        if balance == 0:
            continue
        
        income_statement['revenues'].append({
            'code': account.code,
            'name': account.name,
            'balance': balance
        })
        
        income_statement['total_revenue'] += balance
    
    # Process expense accounts
    for account in expense_accounts:
        # Calculate account balance: Debit - Credit
        balance = db.session.query(func.sum(JournalEntryLine.debit - JournalEntryLine.credit)).\
            join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id).\
            filter(
                JournalEntryLine.account_id == account.id,
                and_(JournalEntry.date >= start_date, JournalEntry.date <= end_date)
            ).scalar() or 0
        
        # Skip accounts with zero balance
        if balance == 0:
            continue
        
        income_statement['expenses'].append({
            'code': account.code,
            'name': account.name,
            'balance': balance
        })
        
        income_statement['total_expense'] += balance
    
    # Calculate net income
    income_statement['net_income'] = income_statement['total_revenue'] - income_statement['total_expense']
    
    return income_statement

def generate_trial_balance(date):
    """
    Generate a trial balance as of a specific date.
    
    Args:
        date (date): The date for which to generate the trial balance
        
    Returns:
        dict: Trial balance data
    """
    # Get all accounts
    accounts = Account.query.order_by(Account.code).all()
    
    # Prepare trial balance structure
    trial_balance = {
        'date': date,
        'accounts': [],
        'total_debit': 0,
        'total_credit': 0
    }
    
    # Process each account
    for account in accounts:
        # Get sum of debits and credits for the account
        debit_sum = db.session.query(func.sum(JournalEntryLine.debit)).\
            join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id).\
            filter(
                JournalEntryLine.account_id == account.id,
                JournalEntry.date <= date
            ).scalar() or 0
        
        credit_sum = db.session.query(func.sum(JournalEntryLine.credit)).\
            join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id).\
            filter(
                JournalEntryLine.account_id == account.id,
                JournalEntry.date <= date
            ).scalar() or 0
        
        # Calculate account balance
        if account.account_type in ['Asset', 'Expense']:
            balance = debit_sum - credit_sum
            debit_balance = balance if balance > 0 else 0
            credit_balance = -balance if balance < 0 else 0
        else:
            balance = credit_sum - debit_sum
            credit_balance = balance if balance > 0 else 0
            debit_balance = -balance if balance < 0 else 0
        
        # Skip accounts with zero balance
        if debit_balance == 0 and credit_balance == 0:
            continue
        
        # Add account to trial balance
        trial_balance['accounts'].append({
            'code': account.code,
            'name': account.name,
            'debit': debit_balance,
            'credit': credit_balance
        })
        
        trial_balance['total_debit'] += debit_balance
        trial_balance['total_credit'] += credit_balance
    
    return trial_balance

def calculate_net_income(start_date, end_date):
    """
    Calculate net income for a specific period.
    
    Args:
        start_date (date): The start date of the period
        end_date (date): The end date of the period
        
    Returns:
        float: Net income
    """
    # Get all revenue accounts (Class 7)
    revenue_accounts = Account.query.filter(Account.code.like('7%')).all()
    revenue_account_ids = [account.id for account in revenue_accounts]
    
    # Get all expense accounts (Class 6)
    expense_accounts = Account.query.filter(Account.code.like('6%')).all()
    expense_account_ids = [account.id for account in expense_accounts]
    
    # Calculate total revenue
    total_revenue = db.session.query(func.sum(JournalEntryLine.credit - JournalEntryLine.debit)).\
        join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id).\
        filter(
            JournalEntryLine.account_id.in_(revenue_account_ids),
            and_(JournalEntry.date >= start_date, JournalEntry.date <= end_date)
        ).scalar() or 0
    
    # Calculate total expenses
    total_expenses = db.session.query(func.sum(JournalEntryLine.debit - JournalEntryLine.credit)).\
        join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id).\
        filter(
            JournalEntryLine.account_id.in_(expense_account_ids),
            and_(JournalEntry.date >= start_date, JournalEntry.date <= end_date)
        ).scalar() or 0
    
    # Net income
    return total_revenue - total_expenses
