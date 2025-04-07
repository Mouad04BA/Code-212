ûfrom flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from models import Invoice, InvoiceLine, TaxDeclaration, JournalEntry
from forms import TaxDeclarationForm
from datetime import datetime
from utils.tax_calculator import calculate_vat, calculate_is, calculate_ir
from sqlalchemy import func

taxes_bp = Blueprint('taxes', __name__, url_prefix='/taxes')

@taxes_bp.route('/')
@login_required
def index():
    return render_template('taxes/index.html', title='Impôts et Taxes')

@taxes_bp.route('/vat')
@login_required
def vat():
    # Get period parameters (default to current month)
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    
    # Calculate VAT details using our utility function
    vat_data = calculate_vat(year, month)
    
    return render_template('taxes/vat.html', 
                          title='TVA',
                          vat_data=vat_data,
                          year=year,
                          month=month)

@taxes_bp.route('/is')
@login_required
def is_tax():
    # Get period parameters (default to current year)
    year = request.args.get('year', datetime.now().year, type=int)
    
    # Calculate IS (Corporate Tax) details
    is_data = calculate_is(year)
    
    return render_template('taxes/is.html', 
                          title='Impôt sur les Sociétés (IS)',
                          is_data=is_data,
                          year=year)

@taxes_bp.route('/ir')
@login_required
def ir_tax():
    # Get period parameters
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    
    # Calculate IR (Income Tax) details
    ir_data = calculate_ir(year, month)
    
    return render_template('taxes/ir.html', 
                          title='Impôt sur le Revenu (IR)',
                          ir_data=ir_data,
                          year=year,
                          month=month)

@taxes_bp.route('/declarations')
@login_required
def declarations():
    declarations = TaxDeclaration.query.order_by(TaxDeclaration.submission_deadline.desc()).all()
    return render_template('taxes/declarations.html', 
                          title='Déclarations fiscales',
                          declarations=declarations)

@taxes_bp.route('/declarations/create', methods=['GET', 'POST'])
@login_required
def create_declaration():
    if not current_user.is_comptable():
        flash('Vous n\'avez pas les droits pour accéder à cette page.', 'danger')
        return redirect(url_for('taxes.declarations'))
    
    form = TaxDeclarationForm()
    
    if form.validate_on_submit():
        # Create the declaration
        declaration = TaxDeclaration(
            declaration_type=form.declaration_type.data,
            period=form.period.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            submission_deadline=form.submission_deadline.data
        )
        
        # Calculate the total amount based on declaration type
        if declaration.declaration_type == 'TVA':
            # Get VAT amounts for the period
            vat_data = calculate_vat(
                declaration.start_date.year, 
                declaration.start_date.month if declaration.period == 'Mensuelle' else None,
                quarter=(declaration.start_date.month - 1) // 3 + 1 if declaration.period == 'Trimestrielle' else None
            )
            declaration.total_amount = vat_data['vat_due']
            
        elif declaration.declaration_type == 'IS':
            # Get IS amounts for the period
            is_data = calculate_is(declaration.start_date.year)
            declaration.total_amount = is_data['total_is']
            
        elif declaration.declaration_type == 'IR':
            # Get IR amounts for the period
            ir_data = calculate_ir(
                declaration.start_date.year,
                declaration.start_date.month if declaration.period == 'Mensuelle' else None
            )
            declaration.total_amount = ir_data['total_ir']
        
        db.session.add(declaration)
        db.session.commit()
        
        flash('La déclaration a été créée avec succès.', 'success')
        return redirect(url_for('taxes.declarations'))
    
    return render_template('taxes/create_declaration.html', 
                          title='Nouvelle déclaration',
                          form=form)

@taxes_bp.route('/declarations/<int:declaration_id>/submit', methods=['POST'])
@login_required
def submit_declaration(declaration_id):
    if not current_user.is_comptable():
        flash('Vous n\'avez pas les droits pour accéder à cette page.', 'danger')
        return redirect(url_for('taxes.declarations'))
    
    declaration = TaxDeclaration.query.get_or_404(declaration_id)
    
    if declaration.submitted:
        flash('Cette déclaration a déjà été soumise.', 'warning')
    else:
        declaration.submitted = True
        declaration.submission_date = datetime.now().date()
        db.session.commit()
        
        flash('La déclaration a été marquée comme soumise avec succès.', 'success')
    
    return redirect(url_for('taxes.declarations'))

@taxes_bp.route('/declarations/<int:declaration_id>/delete', methods=['POST'])
@login_required
def delete_declaration(declaration_id):
    if not current_user.is_comptable():
        flash('Vous n\'avez pas les droits pour accéder à cette page.', 'danger')
        return redirect(url_for('taxes.declarations'))
    
    declaration = TaxDeclaration.query.get_or_404(declaration_id)
    
    if declaration.submitted:
        flash('Vous ne pouvez pas supprimer une déclaration déjà soumise.', 'danger')
    else:
        db.session.delete(declaration)
        db.session.commit()
        
        flash('La déclaration a été supprimée avec succès.', 'success')
    
    return redirect(url_for('taxes.declarations'))

@taxes_bp.route('/vat/rates')
def vat_rates():
    """Return VAT rates used in Morocco"""
    vat_rates = [
        {"rate": 20, "description": "Taux normal"},
        {"rate": 14, "description": "Taux intermédiaire"},
        {"rate": 10, "description": "Taux réduit"},
        {"rate": 7, "description": "Taux spécial"},
        {"rate": 0, "description": "Exonéré"}
    ]
    return jsonify(vat_rates)

@taxes_bp.route('/is/rates')
def is_rates():
    """Return IS (Corporate Tax) rates used in Morocco"""
    is_rates = [
        {"threshold": 0, "rate": 10, "description": "Jusqu'à 300 000 MAD"},
        {"threshold": 300000, "rate": 20, "description": "De 300 001 à 1 000 000 MAD"},
        {"threshold": 1000000, "rate": 31, "description": "Au-delà de 1 000 000 MAD"}
    ]
    return jsonify(is_rates)

@taxes_bp.route('/ir/rates')
def ir_rates():
    """Return IR (Income Tax) rates used in Morocco"""
    ir_rates = [
        {"threshold": 0, "rate": 0, "description": "Jusqu'à 30 000 MAD"},
        {"threshold": 30000, "rate": 10, "description": "De 30 001 à 50 000 MAD"},
        {"threshold": 50000, "rate": 20, "description": "De 50 001 à 60 000 MAD"},
        {"threshold": 60000, "rate": 30, "description": "De 60 001 à 80 000 MAD"},
        {"threshold": 80000, "rate": 34, "description": "De 80 001 à 180 000 MAD"},
        {"threshold": 180000, "rate": 38, "description": "Au-delà de 180 000 MAD"}
    ]
    return jsonify(ir_rates)
