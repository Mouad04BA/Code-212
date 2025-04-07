from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, SelectField, 
    TextAreaField, FloatField, DateField, BooleanField,
    IntegerField, HiddenField, DecimalField
)
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, 
    ValidationError, Optional, NumberRange
)
from models import User, Account

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    submit = SubmitField('Se connecter')

class RegistrationForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired(), Length(min=8)])
    password_confirm = PasswordField('Confirmer mot de passe', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Rôle', choices=[('3', 'Utilisateur')], validators=[DataRequired()]) # Admin can change this
    submit = SubmitField('S\'inscrire')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Ce nom d\'utilisateur est déjà pris. Veuillez en choisir un autre.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Cet email est déjà utilisé. Veuillez en choisir un autre.')

class UserEditForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Rôle', choices=[], validators=[DataRequired()])
    submit = SubmitField('Mettre à jour')

class AccountForm(FlaskForm):
    code = StringField('Code', validators=[DataRequired(), Length(max=20)])
    name = StringField('Nom', validators=[DataRequired(), Length(max=200)])
    account_class = SelectField('Classe', choices=[(1, '1 - Comptes de financement permanent'), 
                                                 (2, '2 - Comptes d\'actif immobilisé'),
                                                 (3, '3 - Comptes d\'actif circulant'),
                                                 (4, '4 - Comptes de passif circulant'),
                                                 (5, '5 - Comptes de trésorerie'),
                                                 (6, '6 - Comptes de charges'),
                                                 (7, '7 - Comptes de produits')], 
                              validators=[DataRequired()], coerce=int)
    account_type = SelectField('Type', choices=[('Asset', 'Actif'), 
                                              ('Liability', 'Passif'),
                                              ('Equity', 'Capitaux propres'),
                                              ('Revenue', 'Produit'),
                                              ('Expense', 'Charge')], 
                             validators=[DataRequired()])
    parent_id = SelectField('Compte parent', choices=[], validators=[Optional()], coerce=int)
    submit = SubmitField('Enregistrer')

class ClientForm(FlaskForm):
    name = StringField('Nom', validators=[DataRequired(), Length(max=100)])
    ice = StringField('ICE', validators=[Optional(), Length(max=20)])
    address = TextAreaField('Adresse', validators=[Optional(), Length(max=200)])
    phone = StringField('Téléphone', validators=[Optional(), Length(max=20)])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=100)])
    submit = SubmitField('Enregistrer')

class SupplierForm(FlaskForm):
    name = StringField('Nom', validators=[DataRequired(), Length(max=100)])
    ice = StringField('ICE', validators=[Optional(), Length(max=20)])
    address = TextAreaField('Adresse', validators=[Optional(), Length(max=200)])
    phone = StringField('Téléphone', validators=[Optional(), Length(max=20)])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=100)])
    submit = SubmitField('Enregistrer')

class JournalEntryForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    reference = StringField('Référence', validators=[Optional(), Length(max=50)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Enregistrer')

class JournalEntryLineForm(FlaskForm):
    account_id = SelectField('Compte', validators=[DataRequired()], coerce=int)
    debit = FloatField('Débit', validators=[Optional(), NumberRange(min=0)])
    credit = FloatField('Crédit', validators=[Optional(), NumberRange(min=0)])
    description = StringField('Description', validators=[Optional(), Length(max=255)])

class InvoiceForm(FlaskForm):
    invoice_type = SelectField('Type', choices=[('client', 'Client'), ('supplier', 'Fournisseur')], validators=[DataRequired()])
    invoice_number = StringField('Numéro de facture', validators=[DataRequired(), Length(max=50)])
    date = DateField('Date', validators=[DataRequired()])
    due_date = DateField('Date d\'échéance', validators=[Optional()])
    client_id = SelectField('Client', validators=[Optional()], coerce=int)
    supplier_id = SelectField('Fournisseur', validators=[Optional()], coerce=int)
    submit = SubmitField('Enregistrer')

class InvoiceLineForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired(), Length(max=255)])
    quantity = FloatField('Quantité', validators=[DataRequired(), NumberRange(min=0.01)])
    unit_price = FloatField('Prix unitaire', validators=[DataRequired(), NumberRange(min=0)])
    tva_rate = SelectField('Taux TVA', choices=[(20, '20%'), (14, '14%'), (10, '10%'), (7, '7%'), (0, '0%')], validators=[DataRequired()], coerce=float)
    
class TaxDeclarationForm(FlaskForm):
    declaration_type = SelectField('Type de déclaration', choices=[
        ('TVA', 'TVA'), 
        ('IS', 'IS - Impôt sur les sociétés'), 
        ('IR', 'IR - Impôt sur le revenu')
    ], validators=[DataRequired()])
    period = SelectField('Période', choices=[
        ('Mensuelle', 'Mensuelle'), 
        ('Trimestrielle', 'Trimestrielle'), 
        ('Annuelle', 'Annuelle')
    ], validators=[DataRequired()])
    start_date = DateField('Date de début', validators=[DataRequired()])
    end_date = DateField('Date de fin', validators=[DataRequired()])
    submission_deadline = DateField('Date limite de dépôt', validators=[DataRequired()])
    submit = SubmitField('Générer la déclaration')

class DeadlineForm(FlaskForm):
    title = StringField('Titre', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=255)])
    due_date = DateField('Date d\'échéance', validators=[DataRequired()])
    deadline_type = SelectField('Type', choices=[
        ('Tax', 'Impôt'), 
        ('Invoice', 'Facture'), 
        ('CNSS', 'CNSS'),
        ('Other', 'Autre')
    ], validators=[DataRequired()])
    submit = SubmitField('Enregistrer')

class ExportForm(FlaskForm):
    report_type = SelectField('Type de rapport', choices=[
        ('journal', 'Journal'), 
        ('ledger', 'Grand Livre'),
        ('balance_sheet', 'Bilan'),
        ('income_statement', 'CPC'),
        ('vat', 'TVA')
    ], validators=[DataRequired()])
    format_type = SelectField('Format', choices=[
        ('pdf', 'PDF'), 
        ('excel', 'Excel')
    ], validators=[DataRequired()])
    start_date = DateField('Date de début', validators=[DataRequired()])
    end_date = DateField('Date de fin', validators=[DataRequired()])
    submit = SubmitField('Exporter')
