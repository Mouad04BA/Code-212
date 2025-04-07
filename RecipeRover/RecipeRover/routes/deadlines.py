from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from models import Deadline, Notification, User
from forms import DeadlineForm
from datetime import datetime, timedelta
from sqlalchemy import and_

deadlines_bp = Blueprint('deadlines', __name__, url_prefix='/deadlines')

@deadlines_bp.route('/')
@login_required
def index():
    deadlines = Deadline.query.order_by(Deadline.due_date).all()
    return render_template('deadlines/index.html', 
                          title='Échéances',
                          deadlines=deadlines)

@deadlines_bp.route('/calendar')
@login_required
def calendar():
    # Get month and year parameters (default to current month/year)
    month = request.args.get('month', datetime.now().month, type=int)
    year = request.args.get('year', datetime.now().year, type=int)
    
    # Get all deadlines for the month
    start_date = datetime(year, month, 1).date()
    if month == 12:
        end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
    
    deadlines = Deadline.query.filter(
        and_(Deadline.due_date >= start_date, Deadline.due_date <= end_date)
    ).all()
    
    # Organize deadlines by day
    calendar_data = {}
    current_date = start_date
    while current_date <= end_date:
        calendar_data[current_date.day] = []
        current_date += timedelta(days=1)
    
    for deadline in deadlines:
        calendar_data[deadline.due_date.day].append(deadline)
    
    return render_template('deadlines/calendar.html', 
                          title='Calendrier des échéances',
                          calendar_data=calendar_data,
                          month=month,
                          year=year,
                          month_name=datetime(year, month, 1).strftime('%B'),
                          days_in_month=(end_date.day),
                          first_day_of_month=start_date.weekday())

@deadlines_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if not current_user.is_comptable():
        flash('Vous n\'avez pas les droits pour accéder à cette page.', 'danger')
        return redirect(url_for('deadlines.index'))
    
    form = DeadlineForm()
    
    if form.validate_on_submit():
        deadline = Deadline(
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data,
            deadline_type=form.deadline_type.data
        )
        
        db.session.add(deadline)
        db.session.commit()
        
        # Create notifications for all users
        users = User.query.all()
        for user in users:
            notification = Notification(
                user_id=user.id,
                title=f"Nouvelle échéance: {deadline.title}",
                message=f"Une nouvelle échéance a été créée pour le {deadline.due_date.strftime('%d/%m/%Y')}.",
                deadline_id=deadline.id
            )
            db.session.add(notification)
        
        db.session.commit()
        
        flash('L\'échéance a été créée avec succès.', 'success')
        return redirect(url_for('deadlines.index'))
    
    return render_template('deadlines/create.html', 
                          title='Nouvelle échéance',
                          form=form)

@deadlines_bp.route('/<int:deadline_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(deadline_id):
    if not current_user.is_comptable():
        flash('Vous n\'avez pas les droits pour accéder à cette page.', 'danger')
        return redirect(url_for('deadlines.index'))
    
    deadline = Deadline.query.get_or_404(deadline_id)
    form = DeadlineForm()
    
    if form.validate_on_submit():
        # Check if due date changed
        due_date_changed = deadline.due_date != form.due_date.data
        
        deadline.title = form.title.data
        deadline.description = form.description.data
        deadline.due_date = form.due_date.data
        deadline.deadline_type = form.deadline_type.data
        
        db.session.commit()
        
        # If due date changed, create notifications
        if due_date_changed:
            users = User.query.all()
            for user in users:
                notification = Notification(
                    user_id=user.id,
                    title=f"Échéance modifiée: {deadline.title}",
                    message=f"La date d'échéance a été modifiée pour le {deadline.due_date.strftime('%d/%m/%Y')}.",
                    deadline_id=deadline.id
                )
                db.session.add(notification)
            
            db.session.commit()
        
        flash('L\'échéance a été mise à jour avec succès.', 'success')
        return redirect(url_for('deadlines.index'))
    
    elif request.method == 'GET':
        form.title.data = deadline.title
        form.description.data = deadline.description
        form.due_date.data = deadline.due_date
        form.deadline_type.data = deadline.deadline_type
    
    return render_template('deadlines/edit.html', 
                          title='Modifier l\'échéance',
                          form=form,
                          deadline=deadline)

@deadlines_bp.route('/<int:deadline_id>/complete', methods=['POST'])
@login_required
def complete(deadline_id):
    if not current_user.is_comptable():
        flash('Vous n\'avez pas les droits pour accéder à cette page.', 'danger')
        return redirect(url_for('deadlines.index'))
    
    deadline = Deadline.query.get_or_404(deadline_id)
    
    deadline.completed = True
    deadline.completed_date = datetime.now().date()
    
    db.session.commit()
    
    # Create notifications for all users
    users = User.query.all()
    for user in users:
        notification = Notification(
            user_id=user.id,
            title=f"Échéance complétée: {deadline.title}",
            message=f"L'échéance du {deadline.due_date.strftime('%d/%m/%Y')} a été marquée comme complétée.",
            deadline_id=deadline.id
        )
        db.session.add(notification)
    
    db.session.commit()
    
    flash('L\'échéance a été marquée comme complétée.', 'success')
    return redirect(url_for('deadlines.index'))

@deadlines_bp.route('/<int:deadline_id>/delete', methods=['POST'])
@login_required
def delete(deadline_id):
    if not current_user.is_comptable():
        flash('Vous n\'avez pas les droits pour accéder à cette page.', 'danger')
        return redirect(url_for('deadlines.index'))
    
    deadline = Deadline.query.get_or_404(deadline_id)
    
    # Delete associated notifications
    Notification.query.filter_by(deadline_id=deadline.id).delete()
    
    db.session.delete(deadline)
    db.session.commit()
    
    flash('L\'échéance a été supprimée avec succès.', 'success')
    return redirect(url_for('deadlines.index'))

@deadlines_bp.route('/notifications')
@login_required
def notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    
    return render_template('deadlines/notifications.html', 
                          title='Notifications',
                          notifications=notifications)

@deadlines_bp.route('/upcoming')
@login_required
def upcoming_deadlines():
    # Get upcoming deadlines (next 30 days)
    today = datetime.now().date()
    end_date = today + timedelta(days=30)
    
    deadlines = Deadline.query.filter(
        and_(Deadline.due_date >= today, Deadline.due_date <= end_date, Deadline.completed == False)
    ).order_by(Deadline.due_date).all()
    
    return jsonify([{
        'id': d.id,
        'title': d.title,
        'type': d.deadline_type,
        'due_date': d.due_date.strftime('%d/%m/%Y'),
        'days_left': (d.due_date - today).days
    } for d in deadlines])
