from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from models import (
    Account, JournalEntry, JournalEntryLine, 
    Client, Supplier, Invoice, InvoiceLine,
    Notification
)
from forms import (
    AccountForm, JournalEntryForm, JournalEntryLineForm,
    ClientForm, SupplierForm, InvoiceForm, InvoiceLineForm
)
from datetime import datetime
from sqlalchemy import func

accounting_bp = Blueprint('accounting', __name__)

@accounting_bp.route('/')
@accounting_bp.route('/dashboard')
@login_required
def dashboard():
    # Get recent journal entries
    recent_entries = JournalEntry.query.order_by(JournalEntry.date.desc()).limit(5).all()
    
    # Get due invoices
    due_invoices = Invoice.query.filter_by(paid=False).filter(Invoice.due_date >= datetime.now().date()).order_by(Invoice.due_date).limit(5).all()
    
    # Get unread notifications
    notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).order_by(Notification.created_at.desc()).limit(10).all()
    
    # Get financial summary
    # Total assets
    total_assets = db.session.query(func.sum(JournalEntryLine.debit - JournalEntryLine.credit)).\
        join(Account, JournalEntryLine.account_id == Account.id).\
        filter(Account.account_type == 'Asset').scalar() or 0
    
    # Total liabilities
    total_liabilities = db.session.query(func.sum(JournalEntryLine.credit - JournalEntryLine.debit)).\
        join(Account, JournalEntryLine.account_id == Account.id).\
        filter(Account.account_type == 'Liability').scalar() or 0
    
    # Total revenue
    total_revenue = db.session.query(func.sum(JournalEntryLine.credit - JournalEntryLine.debit)).\
        join(Account, JournalEntryLine.account_id == Account.id).\
        filter(Account.account_type == 'Revenue').scalar() or 0
    
    # Total expenses
    total_expenses = db.session.query(func.sum(JournalEntryLine.debit - JournalEntryLine.credit)).\
        join(Account, JournalEntryLine.account_id == Account.id).\
        filter(Account.account_type == 'Expense').scalar() or 0
    
    # Net income
    net_income = total_revenue - total_expenses
    
    return render_template('index.html', 
                           title='Tableau de bord',
                           recent_entries=recent_entries,
                           due_invoices=due_invoices,
                           notifications=notifications,
                           total_assets=total_assets,
                           total_liabilities=total_liabilities,
                           total_revenue=total_revenue,
                           total_expenses=total_expenses,
                           net_income=net_income)

# Accounts management
@accounting_bp.route('/accounts')
@login_required
def accounts():
    if not current_user.is_comptable():
        flash('Vous n\'avez pas les droits pour accéder à cette page.', 'danger')
        return redirect(url_for('accounting.dashboard'))
    
    accounts = Account.query.order_by(Account.code).all()
    return render_template('accounting/accounts.html', accounts=accounts, title='Plan comptable')

@accounting_bp.route('/accounts/create', methods=['GET', 'POST'])
@login_required
def create_account():
    if not current_user.is_comptable():
        flash('Vous n\'avez pas les droits pour accéder à cette page.', 'danger')
        return redirect(url_for('accounting.dashboard'))
    
    form = AccountForm()
    # Populate parent account choices
    form.parent_id.choices = [(0, 'Aucun')] + [(a.id, f"{a.code} - {a.name}") for a in Account.query.order_by(Account.code).all()]
    
    if form.validate_on_submit():
        parent_id = form.parent_id.data if form.parent_id.data != 0 else None
        account = Account(
            code=form.code.data,
            name=form.name.data,
            account_class=form.account_class.data,
            account_type=form.account_type.data,
            parent_id=parent_id
        )
        
        db.session.add(account)
        db.session.commit()
        
        flash('Le compte a été créé avec succès.', 'success')
        return redirect(url_for('accounting.accounts'))
    
    return render_template('accounting/create_account.html', form=form, title='Nouveau compte')

@accounting_bp.route('/accounts/<int:account_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_account(account_id):
    if not current_user.is_comptable():
        flash('Vous n\'avez pas les droits pour accéder à cette page.', 'danger')
        return redirect(url_for('accounting.dashboard'))
    
    account = Account.query.get_or_404(account_id)
    form = AccountForm()
    
    # Populate parent account choices (excluding self and children)
    account_ids_to_exclude = [account.id]
    for child in account.children:
        account_ids_to_exclude.append(child.id)
    
    form.parent_id.choices = [(0, 'Aucun')] + [
        (a.id, f"{a.code} - {a.name}") 
        for a in Account.query.filter(~Account.id.in_(account_ids_to_exclude)).order_by(Account.code).all()
    ]
    
    if form.validate_on_submit():
        parent_id = form.parent_id.data if form.parent_id.data != 0 else None
        account.code = form.code.data
        account.name = form.name.data
        account.account_class = form.account_class.data
        account.account_type = form.account_type.data
        account.parent_id = parent_id
        
        db.session.commit()
        
        flash('Le compte a été mis à jour avec succès.', 'success')
        return redirect(url_for('accounting.accounts'))
    
    elif request.method == 'GET':
        form.code.data = account.code
        form.name.data = account.name
        form.account_class.data = account.account_class
        form.account_type.data = account.account_type
        form.parent_id.data = account.parent_id or 0
    
    return render_template('accounting/edit_account.html', form=form, account=account, title='Modifier le compte')

@accounting_bp.route('/accounts/<int:account_id>/delete', methods=['POST'])
@login_required
def delete_account(account_id):
    if not current_user.is_comptable():
        flash('Vous n\'avez pas les droits pour accéder à cette page.', 'danger')
        return redirect(url_for('accounting.dashboard'))
    
    account = Account.query.get_or_404(account_id)
    
    # Check if account has children
    if account.children:
        flash('Ce compte a des sous-comptes et ne peut pas être supprimé.', 'danger')
        return redirect(url_for('accounting.accounts'))
    
    # Check if account is used in journal entries
    entry_lines = JournalEntryLine.query.filter_by(account_id=account.id).first()
    if entry_lines:
        flash('Ce compte est utilisé dans des écritures comptables et ne peut pas être supprimé.', 'danger')
        return redirect(url_for('accounting.accounts'))
    
    db.session.delete(account)
    db.session.commit()
    
    flash('Le compte a été supprimé avec succès.', 'success')
    return redirect(url_for('accounting.accounts'))

# Journal entries management
@accounting_bp.route('/journal')
@login_required
def journal():
    entries = JournalEntry.query.order_by(JournalEntry.date.desc()).all()
    return render_template('accounting/journal.html', entries=entries, title='Journal comptable')

@accounting_bp.route('/journal/create', methods=['GET', 'POST'])
@login_required
def create_journal_entry():
    if not current_user.is_comptable():
        flash('Vous n\'avez pas les droits pour accéder à cette page.', 'danger')
        return redirect(url_for('accounting.journal'))
    
    form = JournalEntryForm()
    
    if form.validate_on_submit():
        # Create journal entry
        entry = JournalEntry(
            date=form.date.data,
            reference=form.reference.data,
            description=form.description.data,
            created_by_id=current_user.id
        )
        
        db.session.add(entry)
        db.session.commit()
        
        flash('L\'écriture a été créée. Ajoutez maintenant les lignes.', 'success')
        return redirect(url_for('accounting.edit_journal_entry', entry_id=entry.id))
    
    return render_template('accounting/create_journal_entry.html', form=form, title='Nouvelle écriture')

@accounting_bp.route('/journal/<int:entry_id>')
@login_required
def view_journal_entry(entry_id):
    entry = JournalEntry.query.get_or_404(entry_id)
    return render_template('accounting/view_journal_entry.html', entry=entry, title='Détail de l\'écriture')

@accounting_bp.route('/journal/<int:entry_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_journal_entry(entry_id):
    if not current_user.is_comptable():
        flash('Vous n\'avez pas les droits pour accéder à cette page.', 'danger')
        return redirect(url_for('accounting.journal'))
    
    entry = JournalEntry.query.get_or_404(entry_id)
    form = JournalEntryForm()
    
    # Line form for adding new lines
    line_form = JournalEntryLineForm()
    line_form.account_id.choices = [(a.id, f"{a.code} - {a.name}") for a in Account.query.order_by(Account.code).all()]
    
    if form.validate_on_submit():
        entry.date = form.date.data
        entry.reference = form.reference.data
        entry.description = form.description.data
        
        db.session.commit()
        
        flash('L\'écriture a été mise à jour avec succès.', 'success')
        return redirect(url_for('accounting.view_journal_entry', entry_id=entry.id))
    
    elif request.method == 'GET':
        form.date.data = entry.date
        form.reference.data = entry.reference
        form.description.data = entry.description
    
    # Calculate totals
    total_debit = sum(line.debit for line in entry.lines)
    total_credit = sum(line.credit for line in entry.lines)
    is_balanced = round(total_debit, 2) == round(total_credit, 2)
    
    return render_template('accounting/edit_journal_entry.html', 
                          form=form, 
                          line_form=line_form,
                          entry=entry, 
                          total_debit=total_debit,
                          total_credit=total_credit,
                          is_balanced=is_balanced,
                          title='Modifier l\'écriture')

@accounting_bp.route('/journal/<int:entry_id>/add_line', methods=['POST'])
@login_required
def add_journal_entry_line(entry_id):
    if not current_user.is_comptable():
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    
    entry = JournalEntry.query.get_or_404(entry_id)
    form = JournalEntryLineForm()
    form.account_id.choices = [(a.id, f"{a.code} - {a.name}") for a in Account.query.order_by(Account.code).all()]
    
    if form.validate_on_submit():
        # Make sure either debit or credit is provided (not both)
        debit = form.debit.data or 0
        credit = form.credit.data or 0
        
        if debit > 0 and credit > 0:
            return jsonify({'status': 'error', 'message': 'Une ligne ne peut pas avoir à la fois un débit et un crédit.'}), 400
        
        line = JournalEntryLine(
            journal_entry_id=entry.id,
            account_id=form.account_id.data,
            debit=debit,
            credit=credit,
            description=form.description.data
        )
        
        db.session.add(line)
        db.session.commit()
        
        # Get account details for response
        account = Account.query.get(form.account_id.data)
        
        return jsonify({
            'status': 'success',
            'message': 'Ligne ajoutée avec succès.',
            'line': {
                'id': line.id,
                'account_code': account.code,
                'account_name': account.name,
                'debit': line.debit,
                'credit': line.credit,
                'description': line.description
            }
        })
    
    errors = {field: err[0] for field, err in form.errors.items()}
    return jsonify({'status': 'error', 'errors': errors}), 400

@accounting_bp.route('/journal/<int:entry_id>/delete_line/<int:line_id>', methods=['POST'])
@login_required
def delete_journal_entry_line(entry_id, line_id):
    if not current_user.is_comptable():
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    
    line = JournalEntryLine.query.filter_by(id=line_id, journal_entry_id=entry_id).first_or_404()
    
    db.session.delete(line)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Ligne supprimée avec succès.'
    })

@accounting_bp.route('/journal/<int:entry_id>/delete', methods=['POST'])
@login_required
def delete_journal_entry(entry_id):
    if not current_user.is_comptable():
        flash('Vous n\'avez pas les droits pour accéder à cette page.', 'danger')
        return redirect(url_for('accounting.journal'))
    
    entry = JournalEntry.query.get_or_404(entry_id)
    
    # Check if entry is linked to an invoice
    invoice = Invoice.query.filter_by(journal_entry_id=entry.id).first()
    if invoice:
        flash('Cette écriture est liée à une facture et ne peut pas être supprimée.', 'danger')
        return redirect(url_for('accounting.journal'))
    
    db.session.delete(entry)
    db.session.commit()
    
    flash('L\'écriture a été supprimée avec succès.', 'success')
    return redirect(url_for('accounting.journal'))

# Client management
@accounting_bp.route('/clients')
@login_required
def clients():
    clients = Client.query.all()
    return render_template('accounting/clients.html', clients=clients, title='Clients')

@accounting_bp.route('/clients/create', methods=['GET', 'POST'])
@login_required
def create_client():
    if not current_user.is_comptable():
        flash('Vous n\'avez pas les droits pour accéder à cette page.', 'danger')
        return redirect(url_for('accounting.clients'))
    
    form = ClientForm()
    
    if form.validate_on_submit():
        client = Client(
            name=form.name.data,
            ice=form.ice.data,
            address=form.address.data,
            phone=form.phone.data,
            email=form.email.data
        )
        
        db.session.add(client)
        db.session.commit()
        
        flash('Le client a été créé avec succès.', 'success')
        return redirect(url_for('accounting.clients'))
    
    return render_template('accounting/create_client.html', form=form, title='Nouveau client')

@accounting_bp.route('/clients/<int:client_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_client(client_id):
    if not current_user.is_comptable():
        flash('Vous n\'avez pas les droits pour accéder à cette page.', 'danger')
        return redirect(url_for('accounting.clients'))
    
    client = Client.query.get_or_404(client_id)
    form = ClientForm()
    
    if form.validate_on_submit():
        client.name = form.name.data
        client.ice = form.ice.data
        client.address = form.address.data
        client.phone = form.phone.data
        client.email = form.email.data
        
        db.session.commit()
        
        flash('Le client a été mis à jour avec succès.', 'success')
        return redirect(url_for('accounting.clients'))
    
    elif request.method == 'GET':
        form.name.data = client.name
        form.ice.data = client.ice
        form.address.data = client.address
        form.phone.data = client.phone
        form.email.data = client.email
    
    return render_template('accounting/edit_client.html', form=form, client=client, title='Modifier le client')

@accounting_bp.route('/clients/<int:client_id>/delete', methods=['POST'])
@login_required
def delete_client(client_id):
    if not current_user.is_comptable():
        flash('Vous n\'avez pas les droits pour accéder à cette page.', 'danger')
        return redirect(url_for('accounting.clients'))
    
    client = Client.query.get_or_404(client_id)
    
    # Check if client has invoices
    if client.invoices:
        flash('Ce client a des factures et ne peut pas être supprimé.', 'danger')
        return redirect(url_for('accounting.clients'))
    
    db.session.delete(client)
    db.session.commit()
    
    flash('Le client a été supprimé avec succès.', 'success')
    return redirect(url_for('accounting.clients'))

# Supplier management
@accounting_bp.route('/suppliers')
@login_required
def suppliers():
    suppliers = Supplier.query.all()
    return render_template('accounting/suppliers.html', suppliers=suppliers, title='Fournisseurs')

@accounting_bp.route('/suppliers/create', methods=['GET', 'POST'])
@login_required
def create_supplier():
    if not current_user.is_comptable():
        flash('Vous n\'avez pas les droits pour accéder à cette page.', 'danger')
        return redirect(url_for('accounting.suppliers'))
    
    form = SupplierForm()
    
    if form.validate_on_submit():
        supplier = Supplier(
            name=form.name.data,
            ice=form.ice.data,
            address=form.address.data,
            phone=form.phone.data,
            email=form.email.data
        )
        
        db.session.add(supplier)
        db.session.commit()
        
        flash('Le fournisseur a été créé avec succès.', 'success')
        return redirect(url_for('accounting.suppliers'))
    
    return render_template('accounting/create_supplier.html', form=form, title='Nouveau fournisseur')

@accounting_bp.route('/suppliers/<int:supplier_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_supplier(supplier_id):
    if not current_user.is_comptable():
        flash('Vous n\'avez pas les droits pour accéder à cette page.', 'danger')
        return redirect(url_for('accounting.suppliers'))
    
    supplier = Supplier.query.get_or_404(supplier_id)
    form = SupplierForm()
    
    if form.validate_on_submit():
        supplier.name = form.name.data
        supplier.ice = form.ice.data
        supplier.address = form.address.data
        supplier.phone = form.phone.data
        supplier.email = form.email.data
        
        db.session.commit()
        
        flash('Le fournisseur a été mis à jour avec succès.', 'success')
        return redirect(url_for('accounting.suppliers'))
    
    elif request.method == 'GET':
        form.name.data = supplier.name
        form.ice.data = supplier.ice
        form.address.data = supplier.address
        form.phone.data = supplier.phone
        form.email.data = supplier.email
    
    return render_template('accounting/edit_supplier.html', form=form, supplier=supplier, title='Modifier le fournisseur')

@accounting_bp.route('/suppliers/<int:supplier_id>/delete', methods=['POST'])
@login_required
def delete_supplier(supplier_id):
    if not current_user.is_comptable():
        flash('Vous n\'avez pas les droits pour accéder à cette page.', 'danger')
        return redirect(url_for('accounting.suppliers'))
    
    supplier = Supplier.query.get_or_404(supplier_id)
    
    # Check if supplier has invoices
    if supplier.invoices:
        flash('Ce fournisseur a des factures et ne peut pas être supprimé.', 'danger')
        return redirect(url_for('accounting.suppliers'))
    
    db.session.delete(supplier)
    db.session.commit()
    
    flash('Le fournisseur a été supprimé avec succès.', 'success')
    return redirect(url_for('accounting.suppliers'))

# Ledger
@accounting_bp.route('/ledger')
@login_required
def ledger():
    accounts = Account.query.order_by(Account.code).all()
    return render_template('accounting/ledger.html', accounts=accounts, title='Grand Livre')

@accounting_bp.route('/ledger/<int:account_id>')
@login_required
def account_ledger(account_id):
    account = Account.query.get_or_404(account_id)
    
    # Get all journal entry lines for this account
    lines = JournalEntryLine.query.filter_by(account_id=account.id).\
        join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id).\
        order_by(JournalEntry.date).all()
    
    # Calculate balance
    balance = 0
    ledger_entries = []
    
    for line in lines:
        if account.account_type in ['Asset', 'Expense']:
            balance += line.debit - line.credit
        else:
            balance += line.credit - line.debit
        
        ledger_entries.append({
            'date': line.journal_entry.date,
            'reference': line.journal_entry.reference,
            'description': line.description or line.journal_entry.description,
            'debit': line.debit,
            'credit': line.credit,
            'balance': balance
        })
    
    return render_template('accounting/account_ledger.html', 
                          account=account, 
                          entries=ledger_entries, 
                          title=f'Grand Livre - {account.code} {account.name}')

# Mark notifications as read
@accounting_bp.route('/notifications/mark_read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first_or_404()
    notification.is_read = True
    db.session.commit()
    
    return jsonify({'status': 'success'})

# Mark all notifications as read
@accounting_bp.route('/notifications/mark_all_read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).all()
    
    for notification in notifications:
        notification.is_read = True
    
    db.session.commit()
    
    return jsonify({'status': 'success'})
