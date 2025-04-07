from app import db
from models import Invoice, InvoiceLine, JournalEntry, JournalEntryLine, Account
from datetime import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy import and_, func

def calculate_vat(year, month=None, quarter=None, end_date=None):
    """
    Calculate VAT for a given period.
    
    Args:
        year (int): The year for which to calculate VAT
        month (int, optional): The month for which to calculate VAT
        quarter (int, optional): The quarter for which to calculate VAT (1-4)
        end_date (date, optional): End date for custom periods
        
    Returns:
        dict: VAT calculation details
    """
    # Determine start and end dates based on inputs
    if month and not quarter:
        # Monthly calculation
        start_date = datetime(year, month, 1).date()
        if end_date:
            end_date = end_date
        else:
            next_month = start_date + relativedelta(months=1)
            end_date = next_month - relativedelta(days=1)
    elif quarter and not month:
        # Quarterly calculation
        start_month = (quarter - 1) * 3 + 1
        start_date = datetime(year, start_month, 1).date()
        if end_date:
            end_date = end_date
        else:
            end_date = start_date + relativedelta(months=3, days=-1)
    else:
        # Default to current month if no specific period is provided
        current_date = datetime.now()
        start_date = datetime(year, current_date.month, 1).date()
        if end_date:
            end_date = end_date
        else:
            next_month = start_date + relativedelta(months=1)
            end_date = next_month - relativedelta(days=1)
    
    # Get all invoices for the period
    client_invoices = Invoice.query.filter(
        and_(
            Invoice.date >= start_date,
            Invoice.date <= end_date,
            Invoice.invoice_type == 'client'
        )
    ).all()
    
    supplier_invoices = Invoice.query.filter(
        and_(
            Invoice.date >= start_date,
            Invoice.date <= end_date,
            Invoice.invoice_type == 'supplier'
        )
    ).all()
    
    # Calculate VAT collected (from client invoices)
    vat_collected = 0
    vat_collected_details = []
    
    for invoice in client_invoices:
        for line in invoice.lines:
            vat_amount = line.total_tva
            vat_collected += vat_amount
            
            vat_collected_details.append({
                'invoice_number': invoice.invoice_number,
                'date': invoice.date,
                'client': invoice.client.name if invoice.client else 'N/A',
                'amount_ht': line.total_ht,
                'tva_rate': line.tva_rate,
                'tva_amount': vat_amount
            })
    
    # Calculate VAT deductible (from supplier invoices)
    vat_deductible = 0
    vat_deductible_details = []
    
    for invoice in supplier_invoices:
        for line in invoice.lines:
            vat_amount = line.total_tva
            vat_deductible += vat_amount
            
            vat_deductible_details.append({
                'invoice_number': invoice.invoice_number,
                'date': invoice.date,
                'supplier': invoice.supplier.name if invoice.supplier else 'N/A',
                'amount_ht': line.total_ht,
                'tva_rate': line.tva_rate,
                'tva_amount': vat_amount
            })
    
    # Calculate VAT due
    vat_due = vat_collected - vat_deductible
    
    # Group data by VAT rate
    vat_collected_by_rate = {}
    vat_deductible_by_rate = {}
    
    for detail in vat_collected_details:
        rate = detail['tva_rate']
        if rate not in vat_collected_by_rate:
            vat_collected_by_rate[rate] = {
                'base_ht': 0,
                'tva': 0
            }
        vat_collected_by_rate[rate]['base_ht'] += detail['amount_ht']
        vat_collected_by_rate[rate]['tva'] += detail['tva_amount']
    
    for detail in vat_deductible_details:
        rate = detail['tva_rate']
        if rate not in vat_deductible_by_rate:
            vat_deductible_by_rate[rate] = {
                'base_ht': 0,
                'tva': 0
            }
        vat_deductible_by_rate[rate]['base_ht'] += detail['amount_ht']
        vat_deductible_by_rate[rate]['tva'] += detail['tva_amount']
    
    return {
        'start_date': start_date,
        'end_date': end_date,
        'vat_collected': vat_collected,
        'vat_collected_details': vat_collected_details,
        'vat_collected_by_rate': vat_collected_by_rate,
        'vat_deductible': vat_deductible,
        'vat_deductible_details': vat_deductible_details,
        'vat_deductible_by_rate': vat_deductible_by_rate,
        'vat_due': vat_due
    }

def calculate_is(year):
    """
    Calculate IS (Corporate Tax) for a given year.
    
    Args:
        year (int): The year for which to calculate IS
        
    Returns:
        dict: IS calculation details
    """
    # Determine fiscal year dates
    start_date = datetime(year, 1, 1).date()
    end_date = datetime(year, 12, 31).date()
    
    # Calculate net income for the period
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
            JournalEntry.date >= start_date,
            JournalEntry.date <= end_date
        ).scalar() or 0
    
    # Calculate total expenses
    total_expenses = db.session.query(func.sum(JournalEntryLine.debit - JournalEntryLine.credit)).\
        join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id).\
        filter(
            JournalEntryLine.account_id.in_(expense_account_ids),
            JournalEntry.date >= start_date,
            JournalEntry.date <= end_date
        ).scalar() or 0
    
    # Net income
    net_income = total_revenue - total_expenses
    
    # Calculate IS based on Moroccan progressive rates
    # 10% for income <= 300,000 MAD
    # 20% for income between 300,001 and 1,000,000 MAD
    # 31% for income > 1,000,000 MAD
    
    is_amount = 0
    is_details = []
    
    if net_income <= 0:
        is_amount = 0
        is_details = [{
            'tranche': '≤ 0 MAD',
            'base': net_income,
            'rate': 0,
            'is': 0
        }]
    else:
        if net_income <= 300000:
            is_amount = net_income * 0.10
            is_details = [{
                'tranche': '≤ 300,000 MAD',
                'base': net_income,
                'rate': 10,
                'is': is_amount
            }]
        elif net_income <= 1000000:
            is_amount = 300000 * 0.10 + (net_income - 300000) * 0.20
            is_details = [
                {
                    'tranche': '≤ 300,000 MAD',
                    'base': 300000,
                    'rate': 10,
                    'is': 300000 * 0.10
                },
                {
                    'tranche': '300,001 - 1,000,000 MAD',
                    'base': net_income - 300000,
                    'rate': 20,
                    'is': (net_income - 300000) * 0.20
                }
            ]
        else:
            is_amount = 300000 * 0.10 + 700000 * 0.20 + (net_income - 1000000) * 0.31
            is_details = [
                {
                    'tranche': '≤ 300,000 MAD',
                    'base': 300000,
                    'rate': 10,
                    'is': 300000 * 0.10
                },
                {
                    'tranche': '300,001 - 1,000,000 MAD',
                    'base': 700000,
                    'rate': 20,
                    'is': 700000 * 0.20
                },
                {
                    'tranche': '> 1,000,000 MAD',
                    'base': net_income - 1000000,
                    'rate': 31,
                    'is': (net_income - 1000000) * 0.31
                }
            ]
    
    return {
        'year': year,
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_income': net_income,
        'is_details': is_details,
        'total_is': is_amount
    }

def calculate_ir(year, month=None):
    """
    Calculate IR (Income Tax) for a given period.
    
    Args:
        year (int): The year for which to calculate IR
        month (int, optional): The month for which to calculate IR
        
    Returns:
        dict: IR calculation details
    """
    # Determine start and end dates based on inputs
    if month:
        # Monthly calculation
        start_date = datetime(year, month, 1).date()
        next_month = start_date + relativedelta(months=1)
        end_date = next_month - relativedelta(days=1)
    else:
        # Annual calculation
        start_date = datetime(year, 1, 1).date()
        end_date = datetime(year, 12, 31).date()
    
    # In a real application, we would need to get salary data
    # Since we don't have a specific salary model in our example,
    # we'll use placeholder calculations for demonstration
    
    # Placeholder for salary data (this would come from a real database)
    # For now, we'll simulate a few employees with salaries
    employees = [
        {'name': 'Employee 1', 'gross_salary': 10000, 'cnss': 400, 'cimr': 300},
        {'name': 'Employee 2', 'gross_salary': 20000, 'cnss': 800, 'cimr': 600},
        {'name': 'Employee 3', 'gross_salary': 30000, 'cnss': 1200, 'cimr': 900}
    ]
    
    ir_details = []
    total_ir = 0
    
    for employee in employees:
        # Calculate net taxable income
        gross_salary = employee['gross_salary']
        cnss = employee['cnss']
        cimr = employee['cimr']
        
        net_taxable = gross_salary - cnss - cimr
        
        # Calculate IR based on Moroccan progressive rates
        # Annual rates converted to monthly if needed
        annual_net = net_taxable * (12 if month else 1)
        
        ir_amount = 0
        
        if annual_net <= 30000:
            ir_amount = 0
        elif annual_net <= 50000:
            ir_amount = (annual_net - 30000) * 0.10
        elif annual_net <= 60000:
            ir_amount = 2000 + (annual_net - 50000) * 0.20
        elif annual_net <= 80000:
            ir_amount = 4000 + (annual_net - 60000) * 0.30
        elif annual_net <= 180000:
            ir_amount = 10000 + (annual_net - 80000) * 0.34
        else:
            ir_amount = 44000 + (annual_net - 180000) * 0.38
        
        # Convert back to monthly if needed
        if month:
            ir_amount = ir_amount / 12
        
        ir_details.append({
            'employee': employee['name'],
            'gross_salary': gross_salary,
            'cnss': cnss,
            'cimr': cimr,
            'net_taxable': net_taxable,
            'ir': ir_amount
        })
        
        total_ir += ir_amount
    
    return {
        'start_date': start_date,
        'end_date': end_date,
        'ir_details': ir_details,
        'total_ir': total_ir
    }
