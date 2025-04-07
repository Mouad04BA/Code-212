from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app import db
from models import User, Role
from forms import LoginForm, RegistrationForm, UserEditForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('accounting.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('accounting.dashboard'))
        else:
            flash('Email ou mot de passe incorrect. Veuillez réessayer.', 'danger')
    
    return render_template('auth/login.html', form=form, title='Connexion')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('accounting.dashboard'))
    
    form = RegistrationForm()
    # Only Admin can create users with Admin or Comptable roles
    if current_user.is_authenticated and current_user.is_admin():
        form.role.choices = [('1', 'Admin'), ('2', 'Comptable'), ('3', 'Utilisateur')]
    
    if form.validate_on_submit():
        role_id = int(form.role.data)
        user = User(
            username=form.username.data,
            email=form.email.data,
            role_id=role_id
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Votre compte a été créé avec succès! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form, title='Inscription')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/users')
@login_required
def users():
    if not current_user.is_admin():
        flash('Vous n\'avez pas les droits pour accéder à cette page.', 'danger')
        return redirect(url_for('accounting.dashboard'))
    
    users = User.query.all()
    return render_template('auth/users.html', users=users, title='Utilisateurs')

@auth_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin():
        flash('Vous n\'avez pas les droits pour accéder à cette page.', 'danger')
        return redirect(url_for('accounting.dashboard'))
    
    user = User.query.get_or_404(user_id)
    form = UserEditForm()
    
    # Populate role choices
    form.role.choices = [(r.id, r.name) for r in Role.query.all()]
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role_id = form.role.data
        
        db.session.commit()
        flash('L\'utilisateur a été mis à jour avec succès.', 'success')
        return redirect(url_for('auth.users'))
    
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.role.data = user.role_id
    
    return render_template('auth/edit_user.html', form=form, user=user, title='Modifier l\'utilisateur')

@auth_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin():
        flash('Vous n\'avez pas les droits pour accéder à cette page.', 'danger')
        return redirect(url_for('accounting.dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('Vous ne pouvez pas supprimer votre propre compte.', 'danger')
        return redirect(url_for('auth.users'))
    
    db.session.delete(user)
    db.session.commit()
    flash('L\'utilisateur a été supprimé avec succès.', 'success')
    return redirect(url_for('auth.users'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UserEditForm()
    
    # Disable role field for non-admin users
    if not current_user.is_admin():
        del form.role
    else:
        form.role.choices = [(r.id, r.name) for r in Role.query.all()]
    
    if form.validate_on_submit():
        if current_user.username != form.username.data:
            # Check if username is already taken
            existing_user = User.query.filter_by(username=form.username.data).first()
            if existing_user and existing_user.id != current_user.id:
                flash('Ce nom d\'utilisateur est déjà pris.', 'danger')
                return render_template('auth/profile.html', form=form, title='Mon profil')
                
        if current_user.email != form.email.data:
            # Check if email is already taken
            existing_user = User.query.filter_by(email=form.email.data).first()
            if existing_user and existing_user.id != current_user.id:
                flash('Cet email est déjà utilisé.', 'danger')
                return render_template('auth/profile.html', form=form, title='Mon profil')
        
        current_user.username = form.username.data
        current_user.email = form.email.data
        
        if current_user.is_admin() and hasattr(form, 'role'):
            current_user.role_id = form.role.data
        
        db.session.commit()
        flash('Votre profil a été mis à jour avec succès.', 'success')
        return redirect(url_for('auth.profile'))
    
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        if hasattr(form, 'role'):
            form.role.data = current_user.role_id
    
    return render_template('auth/profile.html', form=form, title='Mon profil')

# Initialize roles function (will be registered in app.py)
def init_roles():
    # Create default roles if they don't exist
    roles = ['Admin', 'Comptable', 'Utilisateur']
    for role_name in roles:
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name)
            db.session.add(role)
    
    # Create admin user if no users exist
    if User.query.count() == 0:
        admin_role = Role.query.filter_by(name='Admin').first()
        if admin_role:
            admin = User(
                username='admin',
                email='admin@example.com',
                role_id=admin_role.id
            )
            admin.set_password('adminpassword')
            db.session.add(admin)
    
    db.session.commit()
