import os
import hashlib

# --- OpenSSL Monkey-Patch (CRITICAL for xhtml2pdf on Windows) ---
try:
    _original_md5 = hashlib.md5
    def _patched_md5(*args, **kwargs):
        if 'usedforsecurity' in kwargs: 
            kwargs.pop('usedforsecurity')
        return _original_md5(*args, **kwargs)
    hashlib.md5 = _patched_md5
except Exception:
    pass

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, make_response
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from models import db, bcrypt, User, Settings, Submission, Evaluation
from dotenv import load_dotenv
import arabic_reshaper
from bidi.algorithm import get_display


load_dotenv()

app = Flask(__name__, 
            template_folder='../frontend/templates', 
            static_folder='../frontend/static',
            instance_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance'))

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'yly_hr.db')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../frontend/static/uploads')

db.init_app(app)
bcrypt.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Arabic PDF Support ---
def ar_format(text):
    if not text: return ""
    text = str(text)
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text

app.jinja_env.filters['ar'] = ar_format

# --- Error Handlers ---

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

# --- Routes ---

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    settings = Settings.query.first()
    submissions = Submission.query.filter_by(status='pending').all()
    
    # Enriched member data for the new UI
    members_data = []
    all_members = User.query.filter_by(role='member').all()
    for m in all_members:
        # Get approved counts
        m_subs = Submission.query.filter_by(user_id=m.id, status='approved').all()
        m_count = len([s for s in m_subs if s.type == 'meeting'])
        e_count = len([s for s in m_subs if s.type == 'event'])
        t_count = len([s for s in m_subs if s.type == 'task'])
        
        # Get all evaluations for history
        all_evals = Evaluation.query.filter_by(user_id=m.id).order_by(Evaluation.date.desc()).all()
        last_eval = all_evals[0] if all_evals else None
        
        members_data.append({
            'user': m,
            'counts': {'m': m_count, 'e': e_count, 't': t_count},
            'last_eval': last_eval,
            'all_evals': all_evals
        })
        
    return render_template('admin.html', settings=settings, submissions=submissions, members=members_data)

@app.route('/admin/settings', methods=['POST'])
@login_required
def update_settings():
    if current_user.role != 'admin': return redirect(url_for('index'))
    def safe_int(val, default=1):
        try:
            return int(val) if val and str(val).strip() else default
        except (ValueError, TypeError):
            return default

    s.total_meetings = safe_int(request.form.get('total_meetings'), 1)
    s.total_events = safe_int(request.form.get('total_events'), 1)
    s.total_tasks = safe_int(request.form.get('total_tasks'), 1)
    s.technical_max = safe_int(request.form.get('technical_max'), 55)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/submission/<int:id>/approve', methods=['POST'])
@login_required
def approve_submission(id):
    if current_user.role != 'admin': return redirect(url_for('index'))
    sub = Submission.query.get(id)
    sub.status = 'approved'
    db.session.commit()
    flash('تمت الموافقة على الطلب!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/submission/<int:id>/reject', methods=['POST'])
@login_required
def reject_submission(id):
    if current_user.role != 'admin': return redirect(url_for('index'))
    sub = Submission.query.get(id)
    sub.status = 'rejected'
    db.session.commit()
    flash('تم رفض الطلب!', 'error')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/evaluate/<int:user_id>', methods=['POST'])
@login_required
def evaluate_member(user_id):
    if current_user.role != 'admin': return redirect(url_for('index'))
    member = User.query.get(user_id)
    settings = Settings.query.first()
    
    # Calculate Attendance
    subs = Submission.query.filter_by(user_id=user_id, status='approved').all()
    m_count = len([s for s in subs if s.type == 'meeting'])
    e_count = len([s for s in subs if s.type == 'event'])
    t_count = len([s for s in subs if s.type == 'task'])
    
    # Basic Score Logic
    m_target = settings.total_meetings or 1
    e_target = settings.total_events or 1
    t_target = settings.total_tasks or 1
    
    hr_base = (min(float(m_count)/m_target, 1.0) * 20.0 + 
               min(float(e_count)/e_target, 1.0) * 20.0 + 
               min(float(t_count)/t_target, 1.0) * 30.0)
    
    # Manual Scores
    def safe_float(val, default=0.0):
        try:
            return float(val) if val and str(val).strip() else default
        except (ValueError, TypeError):
            return default

    behavior = min(10.0, safe_float(request.form.get('behavior')))
    hierarchy = min(10.0, safe_float(request.form.get('hierarchy'), 10.0))
    group = min(5.0, safe_float(request.form.get('group')))
    follower = min(5.0, safe_float(request.form.get('follower')))
    bonus_head = min(10.0, safe_float(request.form.get('bonus_head')))
    tech = min(settings.technical_max, safe_float(request.form.get('technical')))
    
    # Bonus Logic
    bonus_event = max(0.0, float(e_count - settings.total_events) * 5.0)
    bonus_head = float(request.form.get('bonus_head', 0))
    total_bonus = min(10.0, bonus_event + bonus_head)
    
    hr_score = hr_base + behavior + hierarchy + group + follower + total_bonus
    hr_weighted = (hr_score / 110.0) * 55.0
    total_score = hr_weighted + tech
    
    # Grade
    grade = 'A' if total_score >= 90 else 'B' if total_score >= 75 else 'C' if total_score >= 60 else 'D'
    
    evaluation = Evaluation(user_id=user_id, interaction_group=group, interaction_follower=follower,
                            behavior=behavior, hierarchy=hierarchy, bonus_head=bonus_head,
                            bonus_event=bonus_event, technical_score=tech, hr_score=hr_score, 
                            total_score=total_score, grade=grade, published=False)
    db.session.add(evaluation)
    db.session.commit()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/evaluation/publish/<int:id>', methods=['POST'])
@login_required
def publish_evaluation(id):
    if current_user.role != 'admin': return redirect(url_for('index'))
    eval = Evaluation.query.get(id)
    if eval:
        eval.published = True
        db.session.commit()
        flash('تم نشر التقييم للعضو!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/evaluation/delete/<int:id>', methods=['POST'])
@login_required
def delete_evaluation(id):
    if current_user.role != 'admin': return redirect(url_for('index'))
    eval = Evaluation.query.get(id)
    if eval:
        db.session.delete(eval)
        db.session.commit()
        flash('تم حذف التقييم.', 'error')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/member/create', methods=['POST'])
@login_required
def create_member():
    if current_user.role != 'admin': return redirect(url_for('index'))
    username = request.form.get('username')
    name = request.form.get('name')
    committee = request.form.get('committee')
    password = request.form.get('password', '123456')
    
    if User.query.filter_by(username=username).first():
        flash('اسم المستخدم موجود بالفعل', 'error')
    else:
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_pw, name=name, committee=committee, role='member')
        db.session.add(new_user)
        db.session.commit()
        flash('تم إنشاء العضو بنجاح!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/')
def landing():
    # Serve standalone landing page from frontend folder
    return send_from_directory('../frontend', 'index.html')

@app.route('/home')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('member_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        
        if user:
            if bcrypt.check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('index'))
            else:
                print(f"Login Check: User found '{username}', but password check failed.")
        else:
            print(f"Login Check: User '{username}' not found in database.")
            
        flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/member/dashboard')
@login_required
def member_dashboard():
    settings = Settings.query.first()
    # Calculate scores for the current user
    submissions = Submission.query.filter_by(user_id=current_user.id, status='approved').all()
    meetings = len([s for s in submissions if s.type == 'meeting'])
    events = len([s for s in submissions if s.type == 'event'])
    tasks = len([s for s in submissions if s.type == 'task'])
    
    # Get all PUBLISHED evaluations for history
    evaluations = Evaluation.query.filter_by(user_id=current_user.id, published=True).order_by(Evaluation.date.desc()).all()
    evaluation = evaluations[0] if evaluations else None
    
    return render_template('dashboard.html', settings=settings, eval=evaluation, evaluations=evaluations,
                           counts={'meetings': meetings, 'events': events, 'tasks': tasks})

@app.route('/submit', methods=['POST'])
@login_required
def submit_evidence():
    type = request.form.get('type')
    title = request.form.get('title')
    custom_date = request.form.get('custom_date')
    comment = request.form.get('comment')
    file = request.files.get('screenshot')
    
    # Ensure upload folder exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        
    filename = None
    if file:
        filename = f"{current_user.id}_{type}_{os.urandom(4).hex()}.png"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
    submission = Submission(user_id=current_user.id, type=type, title=title, 
                            custom_date=custom_date, comment=comment, screenshot=filename)
    db.session.add(submission)
    db.session.commit()
    flash('تم إرسال الطلب للمراجعة!', 'success')
    return redirect(url_for('member_dashboard'))

if __name__ == '__main__':
    # Ensure instance folder exists
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)
        
    with app.app_context():
        db.create_all()
        # Create default admin if not exists
        if not User.query.filter_by(username='admin').first():
            hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin = User(username='admin', password=hashed_pw, name='Admin', committee='Central', role='admin')
            db.session.add(admin)
            
        # Create default settings if not exists
        if not Settings.query.first():
            settings = Settings()
            db.session.add(settings)
            
        db.session.commit()
    app.run(debug=True)
