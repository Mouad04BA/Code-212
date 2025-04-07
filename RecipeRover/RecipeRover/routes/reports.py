from flask import Blueprint, render_template, redirect, url_for, flash, request, make_response, jsonify
from flask_login import login_required, current_user
from app import db
from models import Account, JournalEntry, JournalEntryLine
from forms import ExportForm
from utils.report_generator import (
    generate_balance_sheet, 
    generate_income_statement,
    generate_trial_balance
)
from utils.export import export_pdf, export_excel
from datetime import datetime
from sqlalchemy import func, and_

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
@login_required
def index():
    return render_template('reports/index.html', title='Rapports financiers')

@reports_bp.route('/balance_sheet')
@login_required
def balance_sheet():
    # Get date parameter (default to today)
    date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        date = datetime.now().date()
    
    # Generate balance sheet data
    balance_sheet_data = generate_balance_sheet(date)
    
    return render_template('reports/balance_sheet.html', 
                          title='Bilan',
                          balance_sheet=balance_sheet_data,
                          date=date)

@reports_bp.route('/income_statement')
@login_required
def income_statement():
    # Get period parameters
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    # Default to current year if dates not provided
    if not start_date_str:
        start_date = datetime(datetime.now().year, 1, 1).date()
    else:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            start_date = datetime(datetime.now().year, 1, 1).date()
    
    if not end_date_str:
        end_date = datetime.now().date()
    else:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            end_date = datetime.now().date()
    
    # Generate income statement data
    income_statement_data = generate_income_statement(start_date, end_date)
    
    return render_template('reports/income_statement.html', 
                          title='Compte de Produits et Charges (CPC)',
                          income_statement=income_statement_data,
                          start_date=start_date,
                          end_date=end_date)

@reports_bp.route('/trial_balance')
@login_required
def trial_balance():
    # Get date parameter (default to today)
    date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        date = datetime.now().date()
    
    # Generate trial balance data
    trial_balance_data = generate_trial_balance(date)
    
    return render_template('reports/trial_balance.html', 
                          title='Balance de vérification',
                          trial_balance=trial_balance_data,
                          date=date)

@reports_bp.route('/export', methods=['GET', 'POST'])
@login_required
def export():
    form = ExportForm()
    
    if form.validate_on_submit():
        report_type = form.report_type.data
        format_type = form.format_type.data
        start_date = form.start_date.data
        end_date = form.end_date.data
        
        # Generate the appropriate report data
        if report_type == 'balance_sheet':
            report_data = generate_balance_sheet(end_date)
            title = 'Bilan'
        elif report_type == 'income_statement':
            report_data = generate_income_statement(start_date, end_date)
            title = 'Compte de Produits et Charges (CPC)'
        elif report_type == 'journal':
            # Get all journal entries for the period
            entries = JournalEntry.query.filter(
                and_(JournalEntry.date >= start_date, JournalEntry.date <= end_date)
            ).order_by(JournalEntry.date).all()
            report_data = {'entries': entries}
            title = 'Journal Comptable'
        elif report_type == 'ledger':
            # Get all accounts and their entries for the period
            accounts = Account.query.order_by(Account.code).all()
            report_data = {
                'accounts': accounts,
                'start_date': start_date,
                'end_date': end_date
            }
            title = 'Grand Livre'
        elif report_type == 'vat':
            from utils.tax_calculator import calculate_vat
            report_data = calculate_vat(
                start_date.year, 
                start_date.month,
                end_date=end_date
            )
            title = 'État de TVA'
        
        # Generate the export file
        if format_type == 'pdf':
            pdf_data = export_pdf(report_type, report_data, title, start_date, end_date)
            response = make_response(pdf_data)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename={report_type}_{start_date}_{end_date}.pdf'
            return response
        else:  # Excel
            excel_data = export_excel(report_type, report_data, title, start_date, end_date)
            response = make_response(excel_data)
            response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response.headers['Content-Disposition'] = f'attachment; filename={report_type}_{start_date}_{end_date}.xlsx'
            return response
    
    return render_template('reports/export.html', 
                          title='Exporter un rapport',
                          form=form)

@reports_bp.route('/charts/data')
@login_required
def chart_data():
    chart_type = request.args.get('type', 'monthly_revenue_expense')
    
    if chart_type == 'monthly_revenue_expense':
        # Get monthly revenue and expense data for the current year
        year = request.args.get('year', datetime.now().year, type=int)
        
        # Prepare data structure
        months = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                  'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
        revenue_data = [0] * 12
        expense_data = [0] * 12
        
        # Get revenue data by month
        revenue_accounts = Account.query.filter_by(account_type='Revenue').all()
        revenue_account_ids = [account.id for account in revenue_accounts]
        
        for month in range(1, 13):
            # Create date range for the month
            start_date = datetime(year, month, 1).date()
            if month == 12:
                end_date = datetime(year + 1, 1, 1).date()
            else:
                end_date = datetime(year, month + 1, 1).date()
            
            # Query for revenue
            revenue = db.session.query(func.sum(JournalEntryLine.credit - JournalEntryLine.debit)).\
                join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id).\
                filter(
                    JournalEntryLine.account_id.in_(revenue_account_ids),
                    JournalEntry.date >= start_date,
                    JournalEntry.date < end_date
                ).scalar() or 0
            
            revenue_data[month - 1] = round(revenue, 2)
        
        # Get expense data by month
        expense_accounts = Account.query.filter_by(account_type='Expense').all()
        expense_account_ids = [account.id for account in expense_accounts]
        
        for month in range(1, 13):
            # Create date range for the month
            start_date = datetime(year, month, 1).date()
            if month == 12:
                end_date = datetime(year + 1, 1, 1).date()
            else:
                end_date = datetime(year, month + 1, 1).date()
            
            # Query for expenses
            expense = db.session.query(func.sum(JournalEntryLine.debit - JournalEntryLine.credit)).\
                join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id).\
                filter(
                    JournalEntryLine.account_id.in_(expense_account_ids),
                    JournalEntry.date >= start_date,
                    JournalEntry.date < end_date
                ).scalar() or 0
            
            expense_data[month - 1] = round(expense, 2)
        
        return jsonify({
            'labels': months,
            'datasets': [
                {
                    'label': 'Produits',
                    'data': revenue_data,
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    'borderColor': 'rgba(75, 192, 192, 1)',
                    'borderWidth': 1
                },
                {
                    'label': 'Charges',
                    'data': expense_data,
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'borderColor': 'rgba(255, 99, 132, 1)',
                    'borderWidth': 1
                }
            ]
        })
    
    elif chart_type == 'assets_liabilities':
        # Get assets and liabilities data
        assets = db.session.query(func.sum(JournalEntryLine.debit - JournalEntryLine.credit)).\
            join(Account, JournalEntryLine.account_id == Account.id).\
            filter(Account.account_type == 'Asset').scalar() or 0
        
        liabilities = db.session.query(func.sum(JournalEntryLine.credit - JournalEntryLine.debit)).\
            join(Account, JournalEntryLine.account_id == Account.id).\
            filter(Account.account_type == 'Liability').scalar() or 0
        
        equity = db.session.query(func.sum(JournalEntryLine.credit - JournalEntryLine.debit)).\
            join(Account, JournalEntryLine.account_id == Account.id).\
            filter(Account.account_type == 'Equity').scalar() or 0
        
        return jsonify({
            'labels': ['Actifs', 'Passifs', 'Capitaux propres'],
            'datasets': [
                {
                    'data': [round(assets, 2), round(liabilities, 2), round(equity, 2)],
                    'backgroundColor': [
                        'rgba(75, 192, 192, 0.2)',
                        'rgba(255, 99, 132, 0.2)',
                        'rgba(54, 162, 235, 0.2)'
                    ],
                    'borderColor': [
                        'rgba(75, 192, 192, 1)',
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)'
                    ],
                    'borderWidth': 1
                }
            ]
        })
    
    elif chart_type == 'expense_breakdown':
        # Get expense breakdown data
        expense_accounts = Account.query.filter_by(account_type='Expense').all()
        
        labels = []
        data = []
        
        for account in expense_accounts:
            total = db.session.query(func.sum(JournalEntryLine.debit - JournalEntryLine.credit)).\
                filter(JournalEntryLine.account_id == account.id).scalar() or 0
            
            if total > 0:  # Only include accounts with non-zero values
                labels.append(account.name)
                data.append(round(total, 2))
        
        return jsonify({
            'labels': labels,
            'datasets': [
                {
                    'data': data,
                    'backgroundColor': [
                        'rgba(255, 99, 132, 0.2)',
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(255, 206, 86, 0.2)',
                        'rgba(75, 192, 192, 0.2)',
                        'rgba(153, 102, 255, 0.2)',
                        'rgba(255, 159, 64, 0.2)',
                        'rgba(199, 199, 199, 0.2)'
                    ],
                    'borderColor': [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)',
                        'rgba(199, 199, 199, 1)'
                    ],
                    'borderWidth': 1
                }
            ]
        })
    
    return jsonify({'error': 'Invalid chart type'})
