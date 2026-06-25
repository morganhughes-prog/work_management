from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from datetime import datetime, date
from config import Config
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from forms import LoginForm, RegisterForm, TaskForm, AdminClassForm

app = Flask(__name__)
# Load configuration from environment / config.py
app.config.from_object(Config)

# Initialize CSRF protection for all POST requests
csrf = CSRFProtect()
csrf.init_app(app)


@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf, get_file_type_info=get_file_type_info)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- Database Models ---

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    tasks = db.relationship('Task', backref='author', lazy=True)

class WorkClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    
    parent_id = db.Column(db.Integer, db.ForeignKey('work_class.id'), nullable=True)
    children = db.relationship('WorkClass', backref=db.backref('parent', remote_side=[id]), cascade="all, delete-orphan")
    
    tasks = db.relationship('Task', backref='work_class', lazy=True)

    @property
    def full_path(self):
        """Recursively builds the exact path string"""
        if self.parent:
            return f"{self.parent.full_path} > {self.name.title()}"
        return self.name.title()

    @property
    def display_path(self):
        """Truncates the path for clean UI if it exceeds 25 characters"""
        path = self.full_path
        # Only truncate if it's long AND has a parent (top-level classes shouldn't get the '...')
        if len(path) > 25 and self.parent:
            return f"... > {self.name.title()}"
        return path

class Sprint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    end_date = db.Column(db.Date, nullable=True) # <-- NEW
    tasks = db.relationship('Task', backref='sprint', lazy=True)


# (Add this below your ALLOWED_STATUSES)
LIFECYCLE_STAGES = [
    'Discovery / Consult', 
    'Design / Co-Design', 
    'Build / Drafting', 
    'Test / Review', 
    'Approval / Sign Off', 
    'Publish / Handover'
]

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=False, default='TRIAGE')
    lifecycle_stage = db.Column(db.String(100), nullable=False, default='Discovery / Consult') # <-- NEW
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Original creator
    work_class_id = db.Column(db.Integer, db.ForeignKey('work_class.id'), nullable=True)
    assignments = db.relationship('TaskAssignment', backref='task', lazy=True, cascade="all, delete-orphan")
    status_logs = db.relationship('TaskStatusLog', backref='task', lazy=True, cascade="all, delete-orphan")
    attachments = db.relationship('TaskAttachment', backref='task', lazy=True, cascade="all, delete-orphan")
    sprint_id = db.Column(db.Integer, db.ForeignKey('sprint.id'), nullable=True)

class TaskStatusLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    old_status = db.Column(db.String(50), nullable=False)
    new_status = db.Column(db.String(50), nullable=False)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    changed_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    changed_by = db.relationship('User')

# NEW MODEL: The Assignment Ledger
class TaskAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    unassigned_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    user = db.relationship('User')

# NEW MODEL: URL Attachments
class TaskAttachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    label = db.Column(db.String(200), nullable=True)

ALLOWED_STATUSES = ['TRIAGE', 'BACKLOG', 'TO DO', 'DOING', 'RESOLVED']

# Helper function to get file type info from URL
def get_file_type_info(url):
    """Returns a dict with icon emoji, label, and color for a given file URL."""
    url_lower = url.lower()
    
    file_types = {
        # Documents
        'pdf': {'icon': '📄', 'label': 'PDF', 'color': '#dc3545'},
        'doc': {'icon': '📝', 'label': 'Doc', 'color': '#0d6efd'},
        'docx': {'icon': '📝', 'label': 'Doc', 'color': '#0d6efd'},
        'txt': {'icon': '📄', 'label': 'Text', 'color': '#6c757d'},
        
        # Spreadsheets
        'xls': {'icon': '📊', 'label': 'Excel', 'color': '#198754'},
        'xlsx': {'icon': '📊', 'label': 'Excel', 'color': '#198754'},
        'csv': {'icon': '📊', 'label': 'CSV', 'color': '#198754'},
        
        # Presentations
        'ppt': {'icon': '🎬', 'label': 'PowerPoint', 'color': '#fd7e14'},
        'pptx': {'icon': '🎬', 'label': 'PowerPoint', 'color': '#fd7e14'},
        
        # Email
        'msg': {'icon': '✉️', 'label': 'Email', 'color': '#0dcaf0'},
        'eml': {'icon': '✉️', 'label': 'Email', 'color': '#0dcaf0'},
        
        # Archives
        'zip': {'icon': '📦', 'label': 'ZIP', 'color': '#6f42c1'},
        'rar': {'icon': '📦', 'label': 'RAR', 'color': '#6f42c1'},
        '7z': {'icon': '📦', 'label': '7Z', 'color': '#6f42c1'},
        
        # Images
        'jpg': {'icon': '🖼️', 'label': 'Image', 'color': '#e83e8c'},
        'jpeg': {'icon': '🖼️', 'label': 'Image', 'color': '#e83e8c'},
        'png': {'icon': '🖼️', 'label': 'Image', 'color': '#e83e8c'},
        'gif': {'icon': '🖼️', 'label': 'Image', 'color': '#e83e8c'},
        'svg': {'icon': '🖼️', 'label': 'Image', 'color': '#e83e8c'},
        
        # Web
        'html': {'icon': '🌐', 'label': 'HTML', 'color': '#fd7e14'},
        'htm': {'icon': '🌐', 'label': 'HTML', 'color': '#fd7e14'},
        
        # Default
        'default': {'icon': '🔗', 'label': 'Link', 'color': '#6c757d'},
    }
    
    # Extract file extension from URL (ignore query params)
    url_path = url.split('?')[0]
    if '.' in url_path:
        ext = url_path.split('.')[-1].lower()
        return file_types.get(ext, file_types['default'])
    
    return file_types['default']

def add_task_attachments(task_id, attachment_urls_json):
    """Parse JSON array of URLs and create TaskAttachment records."""
    if not attachment_urls_json:
        return
    try:
        urls = json.loads(attachment_urls_json)
        if isinstance(urls, list):
            for url in urls:
                if isinstance(url, dict) and url.get('url'):
                    attachment = TaskAttachment(
                        task_id=task_id, 
                        url=url.get('url').strip(),
                        label=url.get('label', '')
                    )
                    db.session.add(attachment)
            db.session.commit()
    except (json.JSONDecodeError, ValueError):
        pass  # Silently ignore invalid JSON

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Application Routes ---

@app.route('/lifecycle')
@login_required
def lifecycle_board():
    tasks = Task.query.all()
    return render_template('lifecycle_board.html', tasks=tasks, lifecycles=LIFECYCLE_STAGES)

@app.route('/update_lifecycle/<int:task_id>', methods=['POST'])
@login_required
def update_lifecycle(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    new_stage = data.get('lifecycle_stage')
    
    if new_stage in LIFECYCLE_STAGES:
        task.lifecycle_stage = new_stage
        db.session.commit()
        return jsonify({'success': True}), 200
    return jsonify({'success': False, 'error': 'Invalid stage'}), 400

@app.route('/sprints')
@login_required
def sprint_board():
    # Sort sprints chronologically by their end date
    all_sprints = Sprint.query.order_by(Sprint.end_date).all()
    unassigned_tasks = Task.query.filter_by(sprint_id=None).all()
    
    current_date = date.today()
    
    active_sprints = []
    overdue_tasks = []
    
    for sprint in all_sprints:
        # If the sprint's deadline has passed
        if sprint.end_date and sprint.end_date < current_date:
            for task in sprint.tasks:
                # Only pull tasks that are NOT resolved into the spillover bucket
                if task.status != 'RESOLVED':
                    overdue_tasks.append(task)
        else:
            # If the sprint is in the future/present, show it on the board normally
            active_sprints.append(sprint)

    return render_template(
        'sprint_board.html', 
        active_sprints=active_sprints, 
        unassigned_tasks=unassigned_tasks,
        overdue_tasks=overdue_tasks
    )

@app.route('/update_sprint/<int:task_id>', methods=['POST'])
@login_required
def update_sprint(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    new_sprint_id = data.get('sprint_id')
    
    if new_sprint_id == 'unassigned':
        task.sprint_id = None
    else:
        task.sprint_id = int(new_sprint_id)
        
    db.session.commit()
    return jsonify({'success': True}), 200

@app.route('/')
@login_required
def index():
    work_classes = WorkClass.query.all()
    all_users = User.query.all()
    
    # Check board health: How many tasks have no class?
    unclassified_count = Task.query.filter_by(work_class_id=None).count()
    
    # 1. Capture lists for both filters
    filter_class_ids = request.args.getlist('class_id')
    filter_user_ids = request.args.getlist('user_id') 

    query = Task.query

    # 2. Apply Multiple Class Filter (Now with Unclassified Support)
    if filter_class_ids and 'all' not in filter_class_ids:
        class_ids = [int(cid) for cid in filter_class_ids if cid.isdigit()]
        wants_unclassified = 'unclassified' in filter_class_ids
        
        if class_ids and wants_unclassified:
            # Show tasks that match the selected classes OR have no class
            query = query.filter(db.or_(Task.work_class_id.in_(class_ids), Task.work_class_id.is_(None)))
        elif class_ids:
            query = query.filter(Task.work_class_id.in_(class_ids))
        elif wants_unclassified:
            query = query.filter(Task.work_class_id.is_(None))
        
    # 3. Apply Multiple Assigned Users Filter
    if filter_user_ids and 'all' not in filter_user_ids:
        user_ids = [int(uid) for uid in filter_user_ids if uid.isdigit()]
        if user_ids:
            query = query.join(TaskAssignment).filter(
                TaskAssignment.user_id.in_(user_ids),
                TaskAssignment.is_active == True
            ).distinct()
    
    tasks = query.all()
    
    return render_template(
        'index.html', 
        tasks=tasks, 
        statuses=ALLOWED_STATUSES, 
        work_classes=work_classes, 
        all_users=all_users,
        current_class_filters=filter_class_ids, 
        current_user_filters=filter_user_ids,
        unclassified_count=unclassified_count # Pass the health metric to the UI
    )

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_task():
    sprints = Sprint.query.all()
    work_classes = WorkClass.query.all()
    form = TaskForm()
    form.status.choices = [(s, s) for s in ALLOWED_STATUSES]
    form.lifecycle_stage.choices = [(stage, stage) for stage in LIFECYCLE_STAGES]
    form.work_class_id.choices = [('', '-- Unclassified --')] + [(str(c.id), c.full_path) for c in work_classes]
    form.sprint_id.choices = [('', '-- Unassigned --')] + [(str(s.id), s.name) for s in sprints]

    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            status=form.status.data,
            lifecycle_stage=form.lifecycle_stage.data,
            user_id=current_user.id,
            work_class_id=int(form.work_class_id.data) if form.work_class_id.data else None,
            sprint_id=int(form.sprint_id.data) if form.sprint_id.data else None
        )
        db.session.add(task)
        db.session.flush()

        assignment = TaskAssignment(task_id=task.id, user_id=current_user.id)
        db.session.add(assignment)
        db.session.commit()
        
        # Add multiple attachments if provided
        add_task_attachments(task.id, form.attachment_urls_json.data)
        
        return redirect(url_for('index'))

    return render_template('form.html', action="Add", form=form, task=None, sprints=sprints, lifecycles=LIFECYCLE_STAGES)

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    sprints = Sprint.query.all()
    work_classes = WorkClass.query.all()
    all_users = User.query.all() # Fetch all users for the assignment dropdown
    form = TaskForm(obj=task)

    form.status.choices = [(s, s) for s in ALLOWED_STATUSES]
    form.lifecycle_stage.choices = [(stage, stage) for stage in LIFECYCLE_STAGES]
    form.work_class_id.choices = [('', '-- Unclassified --')] + [(str(c.id), c.full_path) for c in work_classes]
    form.sprint_id.choices = [('', '-- Unassigned --')] + [(str(s.id), s.name) for s in sprints]

    if request.method == 'GET':
        form.work_class_id.data = str(task.work_class_id) if task.work_class_id else ''
        form.sprint_id.data = str(task.sprint_id) if task.sprint_id else ''

    if form.validate_on_submit():
        if task.status != form.status.data:
            log = TaskStatusLog(
                task_id=task.id,
                old_status=task.status,
                new_status=form.status.data,
                changed_by_id=current_user.id
            )
            db.session.add(log)

        task.title = form.title.data
        task.description = form.description.data
        task.status = form.status.data
        task.lifecycle_stage = form.lifecycle_stage.data
        task.work_class_id = int(form.work_class_id.data) if form.work_class_id.data else None
        task.sprint_id = int(form.sprint_id.data) if form.sprint_id.data else None

        db.session.commit()
        
        # Add multiple attachments if provided
        add_task_attachments(task.id, form.attachment_urls_json.data)
        
        return redirect(url_for('index'))

    return render_template('form.html', action="Edit", form=form, task=task, all_users=all_users, sprints=sprints, lifecycles=LIFECYCLE_STAGES)

# --- Assignment Routes ---

@app.route('/task/<int:task_id>/assign', methods=['POST'])
@login_required
def assign_user(task_id):
    user_id = request.form.get('user_id')
    if user_id:
        # Check if already actively assigned
        existing = TaskAssignment.query.filter_by(task_id=task_id, user_id=user_id, is_active=True).first()
        if not existing:
            new_assignment = TaskAssignment(task_id=task_id, user_id=user_id)
            db.session.add(new_assignment)
            db.session.commit()
            flash("Mage summoned to task.")
    return redirect(url_for('edit_task', task_id=task_id))

@app.route('/task/<int:task_id>/unassign/<int:assignment_id>', methods=['POST'])
@login_required
def unassign_user(task_id, assignment_id):
    assignment = TaskAssignment.query.get_or_404(assignment_id)
    if assignment.task_id == task_id:
        assignment.is_active = False
        assignment.unassigned_at = datetime.utcnow()
        db.session.commit()
        flash("Mage dismissed from task.")
    return redirect(url_for('edit_task', task_id=task_id))

@app.route('/task/<int:task_id>/attachment/<int:attachment_id>/delete', methods=['POST'])
@login_required
def delete_attachment(task_id, attachment_id):
    attachment = TaskAttachment.query.get_or_404(attachment_id)
    if attachment.task_id == task_id:
        db.session.delete(attachment)
        db.session.commit()
        flash("Attachment removed.")
    return redirect(url_for('edit_task', task_id=task_id))

@app.route('/task/<int:task_id>/attachment/<int:attachment_id>/label', methods=['POST'])
@login_required
def update_attachment_label(task_id, attachment_id):
    print(f'[DEBUG] update_attachment_label called: task_id={task_id}, attachment_id={attachment_id}')
    attachment = TaskAttachment.query.get_or_404(attachment_id)
    print(f'[DEBUG] Attachment found: {attachment}')
    if attachment.task_id != task_id:
        print(f'[DEBUG] Unauthorized access attempt')
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    data = request.get_json()
    print(f'[DEBUG] Request data: {data}')
    new_label = data.get('label', '').strip()
    print(f'[DEBUG] New label: {new_label}')
    attachment.label = new_label if new_label else None
    db.session.commit()
    print(f'[DEBUG] Label saved successfully')
    return jsonify({'success': True, 'label': attachment.label}), 200

# --- Status & Admin Auth Routes ---
@app.route('/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/update_status/<int:task_id>', methods=['POST'])
@login_required
def update_status(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    new_status = data.get('status')
    if new_status in ALLOWED_STATUSES:
        old_status = task.status
        if old_status != new_status:
            task.status = new_status
            log = TaskStatusLog(
                task_id=task.id,
                old_status=old_status,
                new_status=new_status,
                changed_by_id=current_user.id
            )
            db.session.add(log)
        db.session.commit()
        return jsonify({'success': True}), 200
    return jsonify({'success': False, 'error': 'Invalid status'}), 400

@app.route('/admin/classes', methods=['GET', 'POST'])
@login_required
def admin_classes():
    if not current_user.is_admin:
        flash("You do not have the required permissions to enter this sanctum.")
        return redirect(url_for('index'))
        
    classes = WorkClass.query.all()
    classes = sorted(classes, key=lambda c: c.full_path)

    form = AdminClassForm()
    form.parent_id.choices = [('', '-- Top Level (No Parent) --')] + [(str(c.id), c.full_path) for c in classes]

    if form.validate_on_submit():
        name = form.name.data.lower()
        parent_id = int(form.parent_id.data) if form.parent_id.data else None
        
        if name and not WorkClass.query.filter_by(name=name).first():
            new_class = WorkClass(name=name, parent_id=parent_id)
            db.session.add(new_class)
            db.session.commit()
            flash(f"Class '{name}' forged successfully.")
        else:
            flash("Class already exists or name is empty.")
        return redirect(url_for('admin_classes'))

    return render_template('admin_classes.html', classes=classes, form=form)

@app.route('/admin/classes/delete/<int:class_id>', methods=['POST'])
@login_required
def delete_class(class_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    work_class = WorkClass.query.get_or_404(class_id)
    for task in work_class.tasks:
        task.work_class_id = None
    db.session.delete(work_class)
    db.session.commit()
    flash("Class dissolved.")
    return redirect(url_for('admin_classes'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if User.query.filter_by(username=username).first():
            flash('Mage name already registered.')
            return redirect(url_for('register'))
        is_first_user = User.query.count() == 0 
        new_user = User(username=username, password_hash=generate_password_hash(password), is_admin=is_first_user)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('index'))
    return render_template('auth.html', action="Register", form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login failed. Check credentials.')
    return render_template('auth.html', action="Login", form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not WorkClass.query.first():
            default_classes = ['asset', 'workforce', 'governance', 'forums']
            for c in default_classes:
                db.session.add(WorkClass(name=c))
            db.session.commit()
    # In production, run via a WSGI server (gunicorn) and ensure DEBUG is disabled.
    app.run()