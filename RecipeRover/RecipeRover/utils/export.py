import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pandas as pd

def export_pdf(report_type, report_data, title, start_date, end_date):
    """
    Generate a PDF report based on the report type and data.
    
    Args:
        report_type (str): Type of report ('balance_sheet', 'income_statement', etc.)
        report_data (dict): Data for the report
        title (str): Title of the report
        start_date (date): Start date of the report period
        end_date (date): End date of the report period
        
    Returns:
        bytes: PDF data
    """
    buffer = io.BytesIO()
    
    # Create the PDF object
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        rightMargin=30, 
        leftMargin=30, 
        topMargin=30, 
        bottomMargin=30
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Add custom styles
    styles.add(ParagraphStyle(
        name='Title',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,  # Center
        spaceAfter=20
    ))
    
    styles.add(ParagraphStyle(
        name='Subtitle',
        parent=styles['Heading2'],
        fontSize=12,
        alignment=1,  # Center
        spaceAfter=10
    ))
    
    styles.add(ParagraphStyle(
        name='RightAlign',
        parent=styles['Normal'],
        alignment=2  # Right
    ))
    
    # Elements to be added to the PDF
    elements = []
    
    # Add title
    elements.append(Paragraph(title, styles['Title']))
    
    # Add period
    period_text = f"Période: du {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}"
    elements.append(Paragraph(period_text, styles['Subtitle']))
    elements.append(Spacer(1, 20))
    
    # Create report based on type
    if report_type == 'balance_sheet':
        create_balance_sheet_pdf(elements, report_data, styles)
    elif report_type == 'income_statement':
        create_income_statement_pdf(elements, report_data, styles)
    elif report_type == 'journal':
        create_journal_pdf(elements, report_data, styles)
    elif report_type == 'ledger':
        create_ledger_pdf(elements, report_data, styles)
    elif report_type == 'vat':
        create_vat_pdf(elements, report_data, styles)
    
    # Build the PDF
    doc.build(elements)
    
    # Get the PDF value from the buffer
    pdf_value = buffer.getvalue()
    buffer.close()
    
    return pdf_value

def create_balance_sheet_pdf(elements, balance_sheet, styles):
    """Create balance sheet section for PDF"""
    # Assets section
    elements.append(Paragraph("ACTIF", styles['Heading2']))
    elements.append(Spacer(1, 10))
    
    # Non-current assets
    elements.append(Paragraph("Actif immobilisé", styles['Heading3']))
    
    if balance_sheet['assets']['non_current']:
        data = [["Code", "Compte", "Montant (MAD)"]]
        for asset in balance_sheet['assets']['non_current']:
            data.append([asset['code'], asset['name'], f"{asset['balance']:,.2f}"])
        
        data.append(["", "Total actif immobilisé", f"{balance_sheet['assets']['total_non_current']:,.2f}"])
        
        table = Table(data, colWidths=[60, 300, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
        ]))
        
        elements.append(table)
    else:
        elements.append(Paragraph("Aucun actif immobilisé", styles['Normal']))
    
    elements.append(Spacer(1, 10))
    
    # Current assets
    elements.append(Paragraph("Actif circulant", styles['Heading3']))
    
    if balance_sheet['assets']['current']:
        data = [["Code", "Compte", "Montant (MAD)"]]
        for asset in balance_sheet['assets']['current']:
            data.append([asset['code'], asset['name'], f"{asset['balance']:,.2f}"])
        
        data.append(["", "Total actif circulant", f"{balance_sheet['assets']['total_current']:,.2f}"])
        
        table = Table(data, colWidths=[60, 300, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
        ]))
        
        elements.append(table)
    else:
        elements.append(Paragraph("Aucun actif circulant", styles['Normal']))
    
    elements.append(Spacer(1, 10))
    
    # Cash and equivalents
    elements.append(Paragraph("Trésorerie", styles['Heading3']))
    
    if balance_sheet['assets']['cash']:
        data = [["Code", "Compte", "Montant (MAD)"]]
        for asset in balance_sheet['assets']['cash']:
            data.append([asset['code'], asset['name'], f"{asset['balance']:,.2f}"])
        
        data.append(["", "Total trésorerie", f"{balance_sheet['assets']['total_cash']:,.2f}"])
        
        table = Table(data, colWidths=[60, 300, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
        ]))
        
        elements.append(table)
    else:
        elements.append(Paragraph("Aucune trésorerie", styles['Normal']))
    
    elements.append(Spacer(1, 10))
    
    # Total assets
    data = [["TOTAL ACTIF", f"{balance_sheet['assets']['total']:,.2f}"]]
    
    table = Table(data, colWidths=[360, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BOX', (0, 0), (-1, -1), 2, colors.black),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 20))
    
    # Liabilities and equity section
    elements.append(Paragraph("PASSIF", styles['Heading2']))
    elements.append(Spacer(1, 10))
    
    # Equity
    elements.append(Paragraph("Capitaux propres", styles['Heading3']))
    
    if balance_sheet['liabilities']['equity']:
        data = [["Code", "Compte", "Montant (MAD)"]]
        for equity in balance_sheet['liabilities']['equity']:
            data.append([equity.get('code', ''), equity['name'], f"{equity['balance']:,.2f}"])
        
        data.append(["", "Total capitaux propres", f"{balance_sheet['liabilities']['total_equity']:,.2f}"])
        
        table = Table(data, colWidths=[60, 300, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
        ]))
        
        elements.append(table)
    else:
        elements.append(Paragraph("Aucun capitaux propres", styles['Normal']))
    
    elements.append(Spacer(1, 10))
    
    # Non-current liabilities
    elements.append(Paragraph("Passif non courant", styles['Heading3']))
    
    if balance_sheet['liabilities']['non_current']:
        data = [["Code", "Compte", "Montant (MAD)"]]
        for liability in balance_sheet['liabilities']['non_current']:
            data.append([liability['code'], liability['name'], f"{liability['balance']:,.2f}"])
        
        data.append(["", "Total passif non courant", f"{balance_sheet['liabilities']['total_non_current']:,.2f}"])
        
        table = Table(data, colWidths=[60, 300, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
        ]))
        
        elements.append(table)
    else:
        elements.append(Paragraph("Aucun passif non courant", styles['Normal']))
    
    elements.append(Spacer(1, 10))
    
    # Current liabilities
    elements.append(Paragraph("Passif courant", styles['Heading3']))
    
    if balance_sheet['liabilities']['current']:
        data = [["Code", "Compte", "Montant (MAD)"]]
        for liability in balance_sheet['liabilities']['current']:
            data.append([liability['code'], liability['name'], f"{liability['balance']:,.2f}"])
        
        data.append(["", "Total passif courant", f"{balance_sheet['liabilities']['total_current']:,.2f}"])
        
        table = Table(data, colWidths=[60, 300, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
        ]))
        
        elements.append(table)
    else:
        elements.append(Paragraph("Aucun passif courant", styles['Normal']))
    
    elements.append(Spacer(1, 10))
    
    # Total liabilities and equity
    data = [["TOTAL PASSIF", f"{balance_sheet['liabilities']['total']:,.2f}"]]
    
    table = Table(data, colWidths=[360, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BOX', (0, 0), (-1, -1), 2, colors.black),
    ]))
    
    elements.append(table)

def create_income_statement_pdf(elements, income_statement, styles):
    """Create income statement section for PDF"""
    # Revenues section
    elements.append(Paragraph("PRODUITS", styles['Heading2']))
    elements.append(Spacer(1, 10))
    
    if income_statement['revenues']:
        data = [["Code", "Compte", "Montant (MAD)"]]
        for revenue in income_statement['revenues']:
            data.append([revenue['code'], revenue['name'], f"{revenue['balance']:,.2f}"])
        
        data.append(["", "Total des produits", f"{income_statement['total_revenue']:,.2f}"])
        
        table = Table(data, colWidths=[60, 300, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
        ]))
        
        elements.append(table)
    else:
        elements.append(Paragraph("Aucun produit", styles['Normal']))
    
    elements.append(Spacer(1, 20))
    
    # Expenses section
    elements.append(Paragraph("CHARGES", styles['Heading2']))
    elements.append(Spacer(1, 10))
    
    if income_statement['expenses']:
        data = [["Code", "Compte", "Montant (MAD)"]]
        for expense in income_statement['expenses']:
            data.append([expense['code'], expense['name'], f"{expense['balance']:,.2f}"])
        
        data.append(["", "Total des charges", f"{income_statement['total_expense']:,.2f}"])
        
        table = Table(data, colWidths=[60, 300, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
        ]))
        
        elements.append(table)
    else:
        elements.append(Paragraph("Aucune charge", styles['Normal']))
    
    elements.append(Spacer(1, 20))
    
    # Net income
    elements.append(Paragraph("RESULTAT", styles['Heading2']))
    elements.append(Spacer(1, 10))
    
    data = [["Résultat net", f"{income_statement['net_income']:,.2f}"]]
    
    table = Table(data, colWidths=[360, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BOX', (0, 0), (-1, -1), 2, colors.black),
    ]))
    
    elements.append(table)

def create_journal_pdf(elements, journal_data, styles):
    """Create journal section for PDF"""
    elements.append(Paragraph("JOURNAL COMPTABLE", styles['Heading2']))
    elements.append(Spacer(1, 10))
    
    if journal_data['entries']:
        for entry in journal_data['entries']:
            # Entry header
            entry_header = f"Écriture #{entry.id} - {entry.date.strftime('%d/%m/%Y')} - Réf: {entry.reference or 'N/A'}"
            elements.append(Paragraph(entry_header, styles['Heading3']))
            
            if entry.description:
                elements.append(Paragraph(f"Description: {entry.description}", styles['Normal']))
            
            elements.append(Spacer(1, 5))
            
            # Entry lines
            data = [["Compte", "Libellé", "Débit (MAD)", "Crédit (MAD)"]]
            total_debit = 0
            total_credit = 0
            
            for line in entry.lines:
                data.append([
                    f"{line.account.code} - {line.account.name}", 
                    line.description or "", 
                    f"{line.debit:,.2f}" if line.debit > 0 else "", 
                    f"{line.credit:,.2f}" if line.credit > 0 else ""
                ])
                total_debit += line.debit
                total_credit += line.credit
            
            data.append(["", "Totaux", f"{total_debit:,.2f}", f"{total_credit:,.2f}"])
            
            table = Table(data, colWidths=[150, 210, 80, 80])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
                ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOX', (0, 0), (-1, -1), 2, colors.black),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 20))
    else:
        elements.append(Paragraph("Aucune écriture dans le journal", styles['Normal']))

def create_ledger_pdf(elements, ledger_data, styles):
    """Create ledger section for PDF"""
    elements.append(Paragraph("GRAND LIVRE", styles['Heading2']))
    elements.append(Spacer(1, 10))
    
    start_date = ledger_data['start_date']
    end_date = ledger_data['end_date']
    
    if ledger_data['accounts']:
        for account in ledger_data['accounts']:
            # Account header
            account_header = f"{account.code} - {account.name}"
            elements.append(Paragraph(account_header, styles['Heading3']))
            elements.append(Spacer(1, 5))
            
            # Get account entries
            entries_query = (
                "SELECT je.date, je.reference, jel.description, "
                "jel.debit, jel.credit "
                "FROM journal_entry_line jel "
                "JOIN journal_entry je ON jel.journal_entry_id = je.id "
                "WHERE jel.account_id = ? "
                "AND je.date BETWEEN ? AND ? "
                "ORDER BY je.date, je.id"
            )
            
            # This is pseudo-code as we can't execute SQL directly here
            # In a real implementation, we'd use SQLAlchemy or direct database access
            
            # For demonstration, let's create sample data
            from datetime import timedelta
            import random
            
            # Simulate entries
            entries = []
            date = start_date
            balance = 0
            
            while date <= end_date:
                if random.random() > 0.7:  # 30% chance of having an entry on this date
                    debit = random.randint(0, 10000) if random.random() > 0.5 else 0
                    credit = random.randint(0, 10000) if debit == 0 else 0
                    
                    if account.account_type in ['Asset', 'Expense']:
                        balance += debit - credit
                    else:
                        balance += credit - debit
                    
                    entries.append({
                        'date': date,
                        'reference': f'REF-{random.randint(1000, 9999)}',
                        'description': f'Sample transaction on {date}',
                        'debit': debit,
                        'credit': credit,
                        'balance': balance
                    })
                
                date += timedelta(days=random.randint(1, 10))
            
            if entries:
                data = [["Date", "Référence", "Description", "Débit (MAD)", "Crédit (MAD)", "Solde (MAD)"]]
                
                for entry in entries:
                    data.append([
                        entry['date'].strftime('%d/%m/%Y'),
                        entry['reference'],
                        entry['description'],
                        f"{entry['debit']:,.2f}" if entry['debit'] > 0 else "",
                        f"{entry['credit']:,.2f}" if entry['credit'] > 0 else "",
                        f"{entry['balance']:,.2f}"
                    ])
                
                table = Table(data, colWidths=[70, 80, 150, 70, 70, 80])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('ALIGN', (3, 1), (5, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('BOX', (0, 0), (-1, -1), 2, colors.black),
                ]))
                
                elements.append(table)
            else:
                elements.append(Paragraph("Aucune écriture pour ce compte dans la période", styles['Normal']))
            
            elements.append(Spacer(1, 20))
    else:
        elements.append(Paragraph("Aucun compte dans le grand livre", styles['Normal']))

def create_vat_pdf(elements, vat_data, styles):
    """Create VAT report section for PDF"""
    elements.append(Paragraph("ÉTAT DE TVA", styles['Heading2']))
    elements.append(Spacer(1, 10))
    
    # VAT Collected section
    elements.append(Paragraph("TVA Collectée", styles['Heading3']))
    elements.append(Spacer(1, 5))
    
    if vat_data['vat_collected_details']:
        data = [["Facture", "Date", "Client", "Base HT (MAD)", "Taux TVA", "TVA (MAD)"]]
        
        for detail in vat_data['vat_collected_details']:
            data.append([
                detail['invoice_number'],
                detail['date'].strftime('%d/%m/%Y'),
                detail['client'],
                f"{detail['amount_ht']:,.2f}",
                f"{detail['tva_rate']}%",
                f"{detail['tva_amount']:,.2f}"
            ])
        
        data.append(["", "", "", "", "Total TVA collectée", f"{vat_data['vat_collected']:,.2f}"])
        
        table = Table(data, colWidths=[70, 70, 140, 80, 70, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (3, 1), (5, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (5, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
        ]))
        
        elements.append(table)
    else:
        elements.append(Paragraph("Aucune TVA collectée", styles['Normal']))
    
    elements.append(Spacer(1, 20))
    
    # VAT Deductible section
    elements.append(Paragraph("TVA Déductible", styles['Heading3']))
    elements.append(Spacer(1, 5))
    
    if vat_data['vat_deductible_details']:
        data = [["Facture", "Date", "Fournisseur", "Base HT (MAD)", "Taux TVA", "TVA (MAD)"]]
        
        for detail in vat_data['vat_deductible_details']:
            data.append([
                detail['invoice_number'],
                detail['date'].strftime('%d/%m/%Y'),
                detail['supplier'],
                f"{detail['amount_ht']:,.2f}",
                f"{detail['tva_rate']}%",
                f"{detail['tva_amount']:,.2f}"
            ])
        
        data.append(["", "", "", "", "Total TVA déductible", f"{vat_data['vat_deductible']:,.2f}"])
        
        table = Table(data, colWidths=[70, 70, 140, 80, 70, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (3, 1), (5, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (5, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
        ]))
        
        elements.append(table)
    else:
        elements.append(Paragraph("Aucune TVA déductible", styles['Normal']))
    
    elements.append(Spacer(1, 20))
    
    # VAT Summary
    elements.append(Paragraph("Récapitulatif TVA", styles['Heading3']))
    elements.append(Spacer(1, 5))
    
    data = [
        ["TVA collectée", f"{vat_data['vat_collected']:,.2f}"],
        ["TVA déductible", f"{vat_data['vat_deductible']:,.2f}"],
        ["TVA à payer", f"{vat_data['vat_due']:,.2f}"]
    ]
    
    table = Table(data, colWidths=[200, 100])
    table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (1, -1), 'Helvetica-Bold'),
        ('LINEBELOW', (0, 0), (1, 0), 1, colors.black),
        ('LINEBELOW', (0, 1), (1, 1), 1, colors.black),
        ('LINEBELOW', (0, -1), (1, -1), 2, colors.black),
    ]))
    
    elements.append(table)

def export_excel(report_type, report_data, title, start_date, end_date):
    """
    Generate an Excel report based on the report type and data.
    
    Args:
        report_type (str): Type of report ('balance_sheet', 'income_statement', etc.)
        report_data (dict): Data for the report
        title (str): Title of the report
        start_date (date): Start date of the report period
        end_date (date): End date of the report period
        
    Returns:
        bytes: Excel data
    """
    buffer = io.BytesIO()
    
    # Create a pandas Excel writer
    writer = pd.ExcelWriter(buffer, engine='xlsxwriter')
    
    # Create report based on type
    if report_type == 'balance_sheet':
        create_balance_sheet_excel(writer, report_data, title, end_date)
    elif report_type == 'income_statement':
        create_income_statement_excel(writer, report_data, title, start_date, end_date)
    elif report_type == 'journal':
        create_journal_excel(writer, report_data, title, start_date, end_date)
    elif report_type == 'ledger':
        create_ledger_excel(writer, report_data, title, start_date, end_date)
    elif report_type == 'vat':
        create_vat_excel(writer, report_data, title, start_date, end_date)
    
    # Save the Excel file
    writer.close()
    
    # Get the Excel value from the buffer
    excel_value = buffer.getvalue()
    buffer.close()
    
    return excel_value

def create_balance_sheet_excel(writer, balance_sheet, title, date):
    """Create balance sheet worksheet in Excel"""
    # Create DataFrames for each section
    period = f"Au {date.strftime('%d/%m/%Y')}"
    
    # Assets
    non_current_assets = []
    for asset in balance_sheet['assets']['non_current']:
        non_current_assets.append({
            'Code': asset['code'],
            'Compte': asset['name'],
            'Montant (MAD)': asset['balance']
        })
    
    current_assets = []
    for asset in balance_sheet['assets']['current']:
        current_assets.append({
            'Code': asset['code'],
            'Compte': asset['name'],
            'Montant (MAD)': asset['balance']
        })
    
    cash_assets = []
    for asset in balance_sheet['assets']['cash']:
        cash_assets.append({
            'Code': asset['code'],
            'Compte': asset['name'],
            'Montant (MAD)': asset['balance']
        })
    
    # Liabilities and equity
    equity = []
    for item in balance_sheet['liabilities']['equity']:
        equity.append({
            'Code': item.get('code', ''),
            'Compte': item['name'],
            'Montant (MAD)': item['balance']
        })
    
    non_current_liabilities = []
    for liability in balance_sheet['liabilities']['non_current']:
        non_current_liabilities.append({
            'Code': liability['code'],
            'Compte': liability['name'],
            'Montant (MAD)': liability['balance']
        })
    
    current_liabilities = []
    for liability in balance_sheet['liabilities']['current']:
        current_liabilities.append({
            'Code': liability['code'],
            'Compte': liability['name'],
            'Montant (MAD)': liability['balance']
        })
    
    # Create DataFrames
    df_non_current_assets = pd.DataFrame(non_current_assets)
    df_current_assets = pd.DataFrame(current_assets)
    df_cash_assets = pd.DataFrame(cash_assets)
    df_equity = pd.DataFrame(equity)
    df_non_current_liabilities = pd.DataFrame(non_current_liabilities)
    df_current_liabilities = pd.DataFrame(current_liabilities)
    
    # Add total rows
    total_non_current_assets = pd.DataFrame([{
        'Code': '',
        'Compte': 'Total actif immobilisé',
        'Montant (MAD)': balance_sheet['assets']['total_non_current']
    }])
    
    total_current_assets = pd.DataFrame([{
        'Code': '',
        'Compte': 'Total actif circulant',
        'Montant (MAD)': balance_sheet['assets']['total_current']
    }])
    
    total_cash_assets = pd.DataFrame([{
        'Code': '',
        'Compte': 'Total trésorerie',
        'Montant (MAD)': balance_sheet['assets']['total_cash']
    }])
    
    total_assets = pd.DataFrame([{
        'Code': '',
        'Compte': 'TOTAL ACTIF',
        'Montant (MAD)': balance_sheet['assets']['total']
    }])
    
    total_equity = pd.DataFrame([{
        'Code': '',
        'Compte': 'Total capitaux propres',
        'Montant (MAD)': balance_sheet['liabilities']['total_equity']
    }])
    
    total_non_current_liabilities = pd.DataFrame([{
        'Code': '',
        'Compte': 'Total passif non courant',
        'Montant (MAD)': balance_sheet['liabilities']['total_non_current']
    }])
    
    total_current_liabilities = pd.DataFrame([{
        'Code': '',
        'Compte': 'Total passif courant',
        'Montant (MAD)': balance_sheet['liabilities']['total_current']
    }])
    
    total_liabilities = pd.DataFrame([{
        'Code': '',
        'Compte': 'TOTAL PASSIF',
        'Montant (MAD)': balance_sheet['liabilities']['total']
    }])
    
    # Create a workbook and add the balance sheet
    sheet_name = "Bilan"
    
    # Determine starting rows for each section
    row = 0
    
    # Write title and period
    title_df = pd.DataFrame([{'A': title}])
    title_df.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
    row += 1
    
    period_df = pd.DataFrame([{'A': period}])
    period_df.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
    row += 2
    
    # Write assets header
    assets_header = pd.DataFrame([{'A': 'ACTIF'}])
    assets_header.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
    row += 1
    
    # Write non-current assets
    non_current_header = pd.DataFrame([{'A': 'Actif immobilisé'}])
    non_current_header.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
    row += 1
    
    if not df_non_current_assets.empty:
        df_non_current_assets.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False)
        row += len(df_non_current_assets) + 1
        total_non_current_assets.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
        row += 2
    else:
        empty_df = pd.DataFrame([{'A': 'Aucun actif immobilisé'}])
        empty_df.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
        row += 2
    
    # Write current assets
    current_header = pd.DataFrame([{'A': 'Actif circulant'}])
    current_header.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
    row += 1
    
    if not df_current_assets.empty:
        df_current_assets.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False)
        row += len(df_current_assets) + 1
        total_current_assets.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
        row += 2
    else:
        empty_df = pd.DataFrame([{'A': 'Aucun actif circulant'}])
        empty_df.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
        row += 2
    
    # Write cash assets
    cash_header = pd.DataFrame([{'A': 'Trésorerie'}])
    cash_header.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
    row += 1
    
    if not df_cash_assets.empty:
        df_cash_assets.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False)
        row += len(df_cash_assets) + 1
        total_cash_assets.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
        row += 2
    else:
        empty_df = pd.DataFrame([{'A': 'Aucune trésorerie'}])
        empty_df.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
        row += 2
    
    # Write total assets
    total_assets.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
    row += 2
    
    # Write liabilities header
    liabilities_header = pd.DataFrame([{'A': 'PASSIF'}])
    liabilities_header.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
    row += 1
    
    # Write equity
    equity_header = pd.DataFrame([{'A': 'Capitaux propres'}])
    equity_header.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
    row += 1
    
    if not df_equity.empty:
        df_equity.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False)
        row += len(df_equity) + 1
        total_equity.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
        row += 2
    else:
        empty_df = pd.DataFrame([{'A': 'Aucun capitaux propres'}])
        empty_df.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
        row += 2
    
    # Write non-current liabilities
    non_current_liabilities_header = pd.DataFrame([{'A': 'Passif non courant'}])
    non_current_liabilities_header.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
    row += 1
    
    if not df_non_current_liabilities.empty:
        df_non_current_liabilities.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False)
        row += len(df_non_current_liabilities) + 1
        total_non_current_liabilities.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
        row += 2
    else:
        empty_df = pd.DataFrame([{'A': 'Aucun passif non courant'}])
        empty_df.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
        row += 2
    
    # Write current liabilities
    current_liabilities_header = pd.DataFrame([{'A': 'Passif courant'}])
    current_liabilities_header.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
    row += 1
    
    if not df_current_liabilities.empty:
        df_current_liabilities.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False)
        row += len(df_current_liabilities) + 1
        total_current_liabilities.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
        row += 2
    else:
        empty_df = pd.DataFrame([{'A': 'Aucun passif courant'}])
        empty_df.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
        row += 2
    
    # Write total liabilities
    total_liabilities.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
    
    # Auto-adjust columns
    for worksheet in writer.sheets.values():
        worksheet.autofit()

def create_income_statement_excel(writer, income_statement, title, start_date, end_date):
    """Create income statement worksheet in Excel"""
    # Create DataFrames for each section
    period = f"Du {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}"
    
    # Revenues
    revenues = []
    for revenue in income_statement['revenues']:
        revenues.append({
            'Code': revenue['code'],
            'Compte': revenue['name'],
            'Montant (MAD)': revenue['balance']
        })
    
    # Expenses
    expenses = []
    for expense in income_statement['expenses']:
        expenses.append({
            'Code': expense['code'],
            'Compte': expense['name'],
            'Montant (MAD)': expense['balance']
        })
    
    # Create DataFrames
    df_revenues = pd.DataFrame(revenues)
    df_expenses = pd.DataFrame(expenses)
    
    # Add total rows
    total_revenues = pd.DataFrame([{
        'Code': '',
        'Compte': 'Total des produits',
        'Montant (MAD)': income_statement['total_revenue']
    }])
    
    total_expenses = pd.DataFrame([{
        'Code': '',
        'Compte': 'Total des charges',
        'Montant (MAD)': income_statement['total_expense']
    }])
    
    net_income = pd.DataFrame([{
        'Code': '',
        'Compte': 'Résultat net',
        'Montant (MAD)': income_statement['net_income']
    }])
    
    # Create a workbook and add the income statement
    sheet_name = "CPC"
    
    # Determine starting rows for each section
    row = 0
    
    # Write title and period
    title_df = pd.DataFrame([{'A': title}])
    title_df.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
    row += 1
    
    period_df = pd.DataFrame([{'A': period}])
    period_df.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
    row += 2
    
    # Write revenues header
    revenues_header = pd.DataFrame([{'A': 'PRODUITS'}])
    revenues_header.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
    row += 1
    
    if not df_revenues.empty:
        df_revenues.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False)
        row += len(df_revenues) + 1
        total_revenues.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
        row += 2
    else:
        empty_df = pd.DataFrame([{'A': 'Aucun produit'}])
        empty_df.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
        row += 2
    
    # Write expenses header
    expenses_header = pd.DataFrame([{'A': 'CHARGES'}])
    expenses_header.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
    row += 1
    
    if not df_expenses.empty:
        df_expenses.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False)
        row += len(df_expenses) + 1
        total_expenses.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
        row += 2
    else:
        empty_df = pd.DataFrame([{'A': 'Aucune charge'}])
        empty_df.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
        row += 2
    
    # Write net income
    result_header = pd.DataFrame([{'A': 'RESULTAT'}])
    result_header.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
    row += 1
    
    net_income.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
    
    # Auto-adjust columns
    for worksheet in writer.sheets.values():
        worksheet.autofit()

def create_journal_excel(writer, journal_data, title, start_date, end_date):
    """Create journal worksheet in Excel"""
    # Period string
    period = f"Du {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}"
    
    # Create a workbook and add the journal
    sheet_name = "Journal"
    
    # Determine starting rows for each section
    row = 0
    
    # Write title and period
    title_df = pd.DataFrame([{'A': title}])
    title_df.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
    row += 1
    
    period_df = pd.DataFrame([{'A': period}])
    period_df.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
    row += 2
    
    if journal_data['entries']:
        for entry in journal_data['entries']:
            # Entry header
            entry_header = f"Écriture #{entry.id} - {entry.date.strftime('%d/%m/%Y')} - Réf: {entry.reference or 'N/A'}"
            header_df = pd.DataFrame([{'A': entry_header}])
            header_df.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
            row += 1
            
            if entry.description:
                desc_df = pd.DataFrame([{'A': f"Description: {entry.description}"}])
                desc_df.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
                row += 1
            
            # Entry lines
            lines_data = []
            total_debit = 0
            total_credit = 0
            
            for line in entry.lines:
                lines_data.append({
                    'Compte': f"{line.account.code} - {line.account.name}",
                    'Libellé': line.description or "",
                    'Débit (MAD)': line.debit if line.debit > 0 else None,
                    'Crédit (MAD)': line.credit if line.credit > 0 else None
                })
                total_debit += line.debit
                total_credit += line.credit
            
            df_lines = pd.DataFrame(lines_data)
            
            if not df_lines.empty:
                df_lines.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False)
                row += len(df_lines) + 1
                
                # Add totals
                totals_df = pd.DataFrame([{
                    'Compte': '',
                    'Libellé': 'Totaux',
                    'Débit (MAD)': total_debit,
                    'Crédit (MAD)': total_credit
                }])
                
                totals_df.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
                row += 2
            else:
                empty_df = pd.DataFrame([{'A': 'Aucune ligne dans cette écriture'}])
                empty_df.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
                row += 2
    else:
        empty_df = pd.DataFrame([{'A': 'Aucune écriture dans le journal'}])
        empty_df.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
    
    # Auto-adjust columns
    for worksheet in writer.sheets.values():
        worksheet.autofit()

def create_ledger_excel(writer, ledger_data, title, start_date, end_date):
    """Create ledger worksheet in Excel"""
    # Period string
    period = f"Du {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}"
    
    # Create a workbook and add the ledger with one worksheet per account
    if ledger_data['accounts']:
        for account in ledger_data['accounts']:
            sheet_name = f"{account.code}"
            
            # Limit sheet name length (Excel has a 31-character limit)
            if len(sheet_name) > 31:
                sheet_name = sheet_name[:31]
            
            # Determine starting rows for each section
            row = 0
            
            # Write title and period
            title_df = pd.DataFrame([{'A': f"{title} - {account.code} {account.name}"}])
            title_df.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
            row += 1
            
            period_df = pd.DataFrame([{'A': period}])
            period_df.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
            row += 2
            
            # Generate sample entries for demonstration
            # In a real implementation, we'd query the database for actual entries
            from datetime import timedelta
            import random
            
            # Simulate entries
            entries = []
            date = start_date
            balance = 0
            
            while date <= end_date:
                if random.random() > 0.7:  # 30% chance of having an entry on this date
                    debit = random.randint(0, 10000) if random.random() > 0.5 else 0
                    credit = random.randint(0, 10000) if debit == 0 else 0
                    
                    if account.account_type in ['Asset', 'Expense']:
                        balance += debit - credit
                    else:
                        balance += credit - debit
                    
                    entries.append({
                        'Date': date.strftime('%d/%m/%Y'),
                        'Référence': f'REF-{random.randint(1000, 9999)}',
                        'Description': f'Sample transaction on {date}',
                        'Débit (MAD)': debit if debit > 0 else None,
                        'Crédit (MAD)': credit if credit > 0 else None,
                        'Solde (MAD)': balance
                    })
                
                date += timedelta(days=random.randint(1, 10))
            
            if entries:
                df_entries = pd.DataFrame(entries)
                df_entries.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False)
            else:
                empty_df = pd.DataFrame([{'A': 'Aucune écriture pour ce compte dans la période'}])
                empty_df.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
    else:
        # Create a single worksheet if no accounts
        sheet_name = "Grand Livre"
        
        # Write title and period
        title_df = pd.DataFrame([{'A': title}])
        title_df.to_excel(writer, sheet_name=sheet_name, startrow=0, index=False, header=False)
        
        period_df = pd.DataFrame([{'A': period}])
        period_df.to_excel(writer, sheet_name=sheet_name, startrow=1, index=False, header=False)
        
        empty_df = pd.DataFrame([{'A': 'Aucun compte dans le grand livre'}])
        empty_df.to_excel(writer, sheet_name=sheet_name, startrow=3, index=False, header=False)
    
    # Auto-adjust columns
    for worksheet in writer.sheets.values():
        worksheet.autofit()

def create_vat_excel(writer, vat_data, title, start_date, end_date):
    """Create VAT report worksheet in Excel"""
    # Period string
    period = f"Du {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}"
    
    # Create a workbook and add the VAT report
    sheet_name = "TVA"
    
    # Determine starting rows for each section
    row = 0
    
    # Write title and period
    title_df = pd.DataFrame([{'A': title}])
    title_df.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
    row += 1
    
    period_df = pd.DataFrame([{'A': period}])
    period_df.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
    row += 2
    
    # VAT Collected section
    collected_header = pd.DataFrame([{'A': 'TVA Collectée'}])
    collected_header.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
    row += 1
    
    if vat_data['vat_collected_details']:
        collected_data = []
        for detail in vat_data['vat_collected_details']:
            collected_data.append({
                'Facture': detail['invoice_number'],
                'Date': detail['date'].strftime('%d/%m/%Y'),
                'Client': detail['client'],
                'Base HT (MAD)': detail['amount_ht'],
                'Taux TVA': f"{detail['tva_rate']}%",
                'TVA (MAD)': detail['tva_amount']
            })
        
        df_collected = pd.DataFrame(collected_data)
        df_collected.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False)
        row += len(df_collected) + 1
        
        # Add total
        total_collected = pd.DataFrame([{
            'Facture': '',
            'Date': '',
            'Client': '',
            'Base HT (MAD)': '',
            'Taux TVA': 'Total TVA collectée',
            'TVA (MAD)': vat_data['vat_collected']
        }])
        
        total_collected.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
        row += 2
    else:
        empty_df = pd.DataFrame([{'A': 'Aucune TVA collectée'}])
        empty_df.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
        row += 2
    
    # VAT Deductible section
    deductible_header = pd.DataFrame([{'A': 'TVA Déductible'}])
    deductible_header.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
    row += 1
    
    if vat_data['vat_deductible_details']:
        deductible_data = []
        for detail in vat_data['vat_deductible_details']:
            deductible_data.append({
                'Facture': detail['invoice_number'],
                'Date': detail['date'].strftime('%d/%m/%Y'),
                'Fournisseur': detail['supplier'],
                'Base HT (MAD)': detail['amount_ht'],
                'Taux TVA': f"{detail['tva_rate']}%",
                'TVA (MAD)': detail['tva_amount']
            })
        
        df_deductible = pd.DataFrame(deductible_data)
        df_deductible.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False)
        row += len(df_deductible) + 1
        
        # Add total
        total_deductible = pd.DataFrame([{
            'Facture': '',
            'Date': '',
            'Fournisseur': '',
            'Base HT (MAD)': '',
            'Taux TVA': 'Total TVA déductible',
            'TVA (MAD)': vat_data['vat_deductible']
        }])
        
        total_deductible.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
        row += 2
    else:
        empty_df = pd.DataFrame([{'A': 'Aucune TVA déductible'}])
        empty_df.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
        row += 2
    
    # VAT Summary
    summary_header = pd.DataFrame([{'A': 'Récapitulatif TVA'}])
    summary_header.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
    row += 1
    
    summary_data = [
        {'Description': 'TVA collectée', 'Montant (MAD)': vat_data['vat_collected']},
        {'Description': 'TVA déductible', 'Montant (MAD)': vat_data['vat_deductible']},
        {'Description': 'TVA à payer', 'Montant (MAD)': vat_data['vat_due']}
    ]
    
    df_summary = pd.DataFrame(summary_data)
    df_summary.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False)
    
    # Auto-adjust columns
    for worksheet in writer.sheets.values():
        worksheet.autofit()
