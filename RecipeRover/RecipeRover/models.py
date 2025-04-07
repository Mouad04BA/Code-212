from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# User Roles
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    users = db.relationship('User', backref='role', lazy=True)

    def __repr__(self):
        return f"<Role {self.name}>"

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role.name == 'Admin'
    
    def is_comptable(self):
        return self.role.name == 'Comptable' or self.role.name == 'Admin'
    
    def __repr__(self):
        return f"<User {self.username}>"

# Client Model
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ice = db.Column(db.String(20), unique=True, nullable=True)  # ICE = Identifiant Commun de l'Entreprise
    address = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    invoices = db.relationship('Invoice', backref='client', lazy=True)
    
    def __repr__(self):
        return f"<Client {self.name}>"

# Supplier Model
class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ice = db.Column(db.String(20), unique=True, nullable=True)
    address = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    invoices = db.relationship('Invoice', backref='supplier', lazy=True)
    
    def __repr__(self):
        return f"<Supplier {self.name}>"

# Account Model (Plan Comptable Marocain)
class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    account_class = db.Column(db.Integer, nullable=False)  # 1-7 for Moroccan PCM classes
    account_type = db.Column(db.String(50), nullable=True)  # Asset, Liability, Equity, Revenue, Expense
    parent_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=True)
    children = db.relationship('Account', backref=db.backref('parent', remote_side=[id]), lazy=True)
    
    def __repr__(self):
        return f"<Account {self.code} - {self.name}>"

# Journal Entry Model
class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.today)
    reference = db.Column(db.String(50), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_by = db.relationship('User', backref='journal_entries')
    lines = db.relationship('JournalEntryLine', backref='journal_entry', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<JournalEntry {self.id} - {self.date}>"

# Journal Entry Line Model
class JournalEntryLine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    journal_entry_id = db.Column(db.Integer, db.ForeignKey('journal_entry.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    account = db.relationship('Account')
    debit = db.Column(db.Float, default=0.0)
    credit = db.Column(db.Float, default=0.0)
    description = db.Column(db.String(255), nullable=True)
    
    def __repr__(self):
        return f"<JournalEntryLine {self.id} - {self.account.code}>"

# Invoice Model
class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.today)
    due_date = db.Column(db.Date, nullable=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=True)
    invoice_type = db.Column(db.String(20), nullable=False)  # 'client' or 'supplier'
    total_ht = db.Column(db.Float, default=0.0)  # Total without tax
    total_tva = db.Column(db.Float, default=0.0)  # VAT total
    total_ttc = db.Column(db.Float, default=0.0)  # Total with tax
    paid = db.Column(db.Boolean, default=False)
    payment_date = db.Column(db.Date, nullable=True)
    journal_entry_id = db.Column(db.Integer, db.ForeignKey('journal_entry.id'), nullable=True)
    journal_entry = db.relationship('JournalEntry')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    lines = db.relationship('InvoiceLine', backref='invoice', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Invoice {self.invoice_number}>"

# Invoice Line Model
class InvoiceLine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    tva_rate = db.Column(db.Float, nullable=False, default=20.0)  # 20%, 14%, 10%, 7% in Morocco
    total_ht = db.Column(db.Float, nullable=False)
    total_tva = db.Column(db.Float, nullable=False)
    total_ttc = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f"<InvoiceLine {self.id} - {self.description}>"

# Tax Declaration Model
class TaxDeclaration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    declaration_type = db.Column(db.String(20), nullable=False)  # 'TVA', 'IS', 'IR'
    period = db.Column(db.String(20), nullable=False)  # 'Mensuelle', 'Trimestrielle', 'Annuelle'
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    submission_deadline = db.Column(db.Date, nullable=False)
    submitted = db.Column(db.Boolean, default=False)
    submission_date = db.Column(db.Date, nullable=True)
    total_amount = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<TaxDeclaration {self.declaration_type} - {self.period}>"

# Deadline Model
class Deadline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    due_date = db.Column(db.Date, nullable=False)
    deadline_type = db.Column(db.String(50), nullable=False)  # 'Tax', 'Invoice', 'CNSS', etc.
    completed = db.Column(db.Boolean, default=False)
    completed_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Deadline {self.title} - {self.due_date}>"

# Notification Model
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='notifications')
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    deadline_id = db.Column(db.Integer, db.ForeignKey('deadline.id'), nullable=True)
    deadline = db.relationship('Deadline')
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Notification {self.title} for {self.user.username}>"
