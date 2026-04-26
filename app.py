from datetime import datetime
from functools import wraps
import os
import shutil
import sqlite3
import uuid

from flask import Flask, flash, redirect, render_template, request, send_from_directory, session, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename

from models import (
    Certificate,
    DomainContent,
    Product,
    Purchase,
    SiteContent,
    Submission,
    User,
    db,
)

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
basedir = os.path.abspath(os.path.dirname(__file__))
default_upload_dir = os.path.join(basedir, 'static', 'uploads')
default_sqlite_path = os.path.join(basedir, 'briticana.db')


def build_database_uri():
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        return database_url

    sqlite_path = os.environ.get('SQLITE_PATH', default_sqlite_path)
    sqlite_dir = os.path.dirname(sqlite_path)
    if sqlite_dir:
        os.makedirs(sqlite_dir, exist_ok=True)
    if (
        sqlite_path != default_sqlite_path
        and not os.path.exists(sqlite_path)
        and os.path.exists(default_sqlite_path)
    ):
        shutil.copy2(default_sqlite_path, sqlite_path)
    return 'sqlite:///' + sqlite_path


def is_sqlite_uri(database_uri):
    return database_uri.startswith('sqlite:///')


def normalize_admin_prefix(prefix_value):
    cleaned = (prefix_value or '/admin').strip()
    if not cleaned:
        return '/admin'
    if not cleaned.startswith('/'):
        cleaned = '/' + cleaned
    if cleaned != '/' and cleaned.endswith('/'):
        cleaned = cleaned.rstrip('/')
    return cleaned


app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'briticana_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = build_database_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['ADMIN_USERNAME'] = os.environ.get('ADMIN_USERNAME', 'admin')
app.config['ADMIN_PASSWORD'] = os.environ.get('ADMIN_PASSWORD', 'admin123')
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', default_upload_dir)
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['ADMIN_URL_PREFIX'] = normalize_admin_prefix(
    os.environ.get('ADMIN_URL_PREFIX', '/admin')
)

if os.environ.get('RENDER') == 'true' or os.environ.get('PYTHONANYWHERE_SITE'):
    app.config['PREFERRED_URL_SCHEME'] = 'https'
    app.config['SESSION_COOKIE_SECURE'] = True

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}
PRODUCT_STATUS_OPTIONS = ['Open', 'Closed', 'Coming Soon']

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
db.init_app(app)

DEFAULT_SITE_CONTENT = {
    'theme_primary': '#0f172a',
    'theme_secondary': '#2563eb',
    'theme_accent': '#f43f5e',
    'theme_bg_light': '#f8fafc',
    'theme_text_dark': '#0f172a',
    'theme_text_muted': '#475569',
    'logo_image': '/static/images/logo.jpg',
    'hero_badge': 'GUARANTEED VIRTUAL INTERNSHIPS',
    'hero_title': 'Accelerate Your Tech Career with Real-World Projects',
    'hero_description': "Don't just learn theory. Build your professional portfolio by completing industry-standard virtual internships, practical tech projects, and intensive skill sprints. Get verified certificates trusted by top employers.",
    'hero_primary_button_text': 'Explore Programs',
    'hero_secondary_button_text': 'Verify Certificate',
    'hero_image': 'https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=800&q=80',
    'hero_card_one_title': '90-Day Internships',
    'hero_card_one_text': 'Real-world tasks.',
    'hero_card_two_title': 'Verified Portfolios',
    'hero_card_two_text': 'Globally recognized.',
    'domains_title': 'Explore 25+ Career Domains',
    'domains_description': 'From Web Development to Artificial Intelligence, select your preferred career domain and start building your real-world experience today.',
    'internships_title': 'Premium Internships',
    'internships_description': 'Deep, immersive 90-day to 6-month programs.',
    'projects_title': 'Structured Projects',
    'projects_description': 'Complete 3-tiered tasks to build your portfolio.',
    'tasks_title': 'Skill Sprints & Tasks',
    'tasks_description': 'Short 4-25 day sprints to master a specific technology.',
    'default_internship_image': 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=500&q=80',
    'default_project_image': 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=500&q=80',
    'default_task_image': 'https://images.unsplash.com/photo-1516116216624-53e697fedbea?auto=format&fit=crop&w=500&q=80',
    'domain_badge': 'DOMAIN OVERVIEW',
    'domain_default_description': 'Master the required skills for this domain through our structured programs below.',
    'details_enquiry_title': 'Enquire for More Details',
    'details_sidebar_title': 'Ready to start?',
    'details_sidebar_description': 'After completing the payment, you will receive a unique access code to register your account and start your journey.',
    'details_payment_button_text': 'Proceed to Payment',
    'details_payment_note': 'Secure payment via Razorpay',
    'verification_title': 'Certificate Verification',
    'verification_description': 'Verify the authenticity of a Briticana certificate by entering its unique verification code below.',
    'footer_about_title': 'Briticana',
    'footer_about_description': 'Empowering the next generation of professionals with guaranteed, structured internships and real-world projects. Build your portfolio, fast.',
    'footer_links_title': 'Quick Links',
    'footer_legal_title': 'Legal & Contact',
    'privacy_policy_url': '#',
    'privacy_policy_label': 'Privacy Policy',
    'terms_url': '#',
    'terms_label': 'Terms of Service',
    'support_email': 'support@briticana.com',
    'footer_copyright': 'Briticana. All rights reserved.',
    'whatsapp_title': 'Briticana Community',
    'whatsapp_status': 'Usually responds instantly',
    'whatsapp_message': 'Want to get daily updates, project tasks, and connect with other students? Join our official WhatsApp Community!',
    'whatsapp_link': 'https://chat.whatsapp.com/YOUR_INVITE_LINK_HERE',
}

CONTENT_SECTIONS = [
    {
        'title': 'Brand and Theme',
        'description': 'Control logo and front-end color styling without editing CSS.',
        'fields': [
            {'key': 'logo_image', 'label': 'Logo Image URL', 'type': 'text', 'upload_name': 'logo_image_file', 'preview': True},
            {'key': 'theme_primary', 'label': 'Primary Color', 'type': 'color'},
            {'key': 'theme_secondary', 'label': 'Secondary Color', 'type': 'color'},
            {'key': 'theme_accent', 'label': 'Accent Color', 'type': 'color'},
            {'key': 'theme_bg_light', 'label': 'Background Color', 'type': 'color'},
            {'key': 'theme_text_dark', 'label': 'Main Text Color', 'type': 'color'},
            {'key': 'theme_text_muted', 'label': 'Muted Text Color', 'type': 'color'},
        ],
    },
    {
        'title': 'Homepage Hero',
        'description': 'Update the headline, call to action, and hero section imagery.',
        'fields': [
            {'key': 'hero_badge', 'label': 'Badge', 'type': 'text'},
            {'key': 'hero_title', 'label': 'Title', 'type': 'textarea', 'rows': 2},
            {'key': 'hero_description', 'label': 'Description', 'type': 'textarea', 'rows': 4},
            {'key': 'hero_primary_button_text', 'label': 'Primary Button Text', 'type': 'text'},
            {'key': 'hero_secondary_button_text', 'label': 'Secondary Button Text', 'type': 'text'},
            {'key': 'hero_image', 'label': 'Hero Image URL', 'type': 'text', 'upload_name': 'hero_image_file', 'preview': True},
            {'key': 'hero_card_one_title', 'label': 'Hero Card 1 Title', 'type': 'text'},
            {'key': 'hero_card_one_text', 'label': 'Hero Card 1 Text', 'type': 'text'},
            {'key': 'hero_card_two_title', 'label': 'Hero Card 2 Title', 'type': 'text'},
            {'key': 'hero_card_two_text', 'label': 'Hero Card 2 Text', 'type': 'text'},
        ],
    },
    {
        'title': 'Homepage Sections and Default Images',
        'description': 'Edit section titles and the fallback images used across internships, projects, and tasks.',
        'fields': [
            {'key': 'domains_title', 'label': 'Domains Title', 'type': 'text'},
            {'key': 'domains_description', 'label': 'Domains Description', 'type': 'textarea', 'rows': 3},
            {'key': 'internships_title', 'label': 'Internships Title', 'type': 'text'},
            {'key': 'internships_description', 'label': 'Internships Description', 'type': 'textarea', 'rows': 2},
            {'key': 'default_internship_image', 'label': 'Default Internship Image URL', 'type': 'text', 'upload_name': 'default_internship_image_file', 'preview': True},
            {'key': 'projects_title', 'label': 'Projects Title', 'type': 'text'},
            {'key': 'projects_description', 'label': 'Projects Description', 'type': 'textarea', 'rows': 2},
            {'key': 'default_project_image', 'label': 'Default Project Image URL', 'type': 'text', 'upload_name': 'default_project_image_file', 'preview': True},
            {'key': 'tasks_title', 'label': 'Tasks Title', 'type': 'text'},
            {'key': 'tasks_description', 'label': 'Tasks Description', 'type': 'textarea', 'rows': 2},
            {'key': 'default_task_image', 'label': 'Default Task Image URL', 'type': 'text', 'upload_name': 'default_task_image_file', 'preview': True},
        ],
    },
    {
        'title': 'Domain and Details Pages',
        'description': 'Manage shared text used on domain pages and product details pages.',
        'fields': [
            {'key': 'domain_badge', 'label': 'Domain Badge', 'type': 'text'},
            {'key': 'domain_default_description', 'label': 'Domain Default Description', 'type': 'textarea', 'rows': 3},
            {'key': 'details_enquiry_title', 'label': 'Enquiry Section Title', 'type': 'text'},
            {'key': 'details_sidebar_title', 'label': 'Sidebar Title', 'type': 'text'},
            {'key': 'details_sidebar_description', 'label': 'Sidebar Description', 'type': 'textarea', 'rows': 3},
            {'key': 'details_payment_button_text', 'label': 'Payment Button Text', 'type': 'text'},
            {'key': 'details_payment_note', 'label': 'Payment Note', 'type': 'text'},
        ],
    },
    {
        'title': 'Verification and Footer',
        'description': 'Update certificate verification copy, support email, legal links, and footer text.',
        'fields': [
            {'key': 'verification_title', 'label': 'Verification Title', 'type': 'text'},
            {'key': 'verification_description', 'label': 'Verification Description', 'type': 'textarea', 'rows': 3},
            {'key': 'footer_about_title', 'label': 'Footer Brand Title', 'type': 'text'},
            {'key': 'footer_about_description', 'label': 'Footer Brand Description', 'type': 'textarea', 'rows': 3},
            {'key': 'footer_links_title', 'label': 'Footer Links Title', 'type': 'text'},
            {'key': 'footer_legal_title', 'label': 'Footer Legal Title', 'type': 'text'},
            {'key': 'privacy_policy_label', 'label': 'Privacy Policy Label', 'type': 'text'},
            {'key': 'privacy_policy_url', 'label': 'Privacy Policy URL', 'type': 'text'},
            {'key': 'terms_label', 'label': 'Terms Label', 'type': 'text'},
            {'key': 'terms_url', 'label': 'Terms URL', 'type': 'text'},
            {'key': 'support_email', 'label': 'Support Email', 'type': 'text'},
            {'key': 'footer_copyright', 'label': 'Footer Copyright', 'type': 'text'},
        ],
    },
    {
        'title': 'WhatsApp Widget',
        'description': 'Control the floating community box shown across the website.',
        'fields': [
            {'key': 'whatsapp_title', 'label': 'Widget Title', 'type': 'text'},
            {'key': 'whatsapp_status', 'label': 'Widget Status', 'type': 'text'},
            {'key': 'whatsapp_message', 'label': 'Widget Message', 'type': 'textarea', 'rows': 4},
            {'key': 'whatsapp_link', 'label': 'WhatsApp Invite Link', 'type': 'text'},
        ],
    },
]

SITE_FIELD_MAP = {
    field['key']: field
    for section in CONTENT_SECTIONS
    for field in section['fields']
}


def ensure_database_schema():
    if not is_sqlite_uri(app.config['SQLALCHEMY_DATABASE_URI']):
        return

    with db.engine.begin() as connection:
        product_columns = {
            row[1]
            for row in connection.exec_driver_sql("PRAGMA table_info(product)").fetchall()
        }
        if 'availability_status' not in product_columns:
            connection.exec_driver_sql(
                "ALTER TABLE product ADD COLUMN availability_status VARCHAR(30) DEFAULT 'Open'"
            )
        if 'image_url' not in product_columns:
            connection.exec_driver_sql(
                "ALTER TABLE product ADD COLUMN image_url VARCHAR(400)"
            )


def parse_snapshot_datetime(value):
    if not value:
        return None

    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            for fmt in ('%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S'):
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue

    return None


def get_snapshot_rows(cursor, table_name):
    exists = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    if not exists:
        return []
    return cursor.execute(f"SELECT * FROM {table_name}").fetchall()


def seed_database_from_local_snapshot():
    if not os.environ.get('DATABASE_URL'):
        return

    if not os.path.exists(default_sqlite_path):
        return

    if any([
        Product.query.first(),
        SiteContent.query.first(),
        DomainContent.query.first(),
        User.query.first(),
    ]):
        return

    source_connection = sqlite3.connect(default_sqlite_path)
    source_connection.row_factory = sqlite3.Row

    try:
        cursor = source_connection.cursor()
        domain_rows = get_snapshot_rows(cursor, 'domain_content')
        site_content_rows = get_snapshot_rows(cursor, 'site_content')
        user_rows = get_snapshot_rows(cursor, 'user')
        product_rows = get_snapshot_rows(cursor, 'product')
        purchase_rows = get_snapshot_rows(cursor, 'purchase')
        submission_rows = get_snapshot_rows(cursor, 'submission')
        certificate_rows = get_snapshot_rows(cursor, 'certificate')

        for row in domain_rows:
            db.session.merge(
                DomainContent(
                    id=row['id'],
                    name=row['name'],
                    badge=row['badge'],
                    headline=row['headline'],
                    description=row['description'],
                    created_at=parse_snapshot_datetime(row['created_at']) or datetime.utcnow(),
                )
            )

        for row in site_content_rows:
            db.session.merge(
                SiteContent(
                    key=row['key'],
                    value=row['value'] or '',
                    updated_at=parse_snapshot_datetime(row['updated_at']) or datetime.utcnow(),
                )
            )

        for row in user_rows:
            db.session.merge(
                User(
                    id=row['id'],
                    unique_code=row['unique_code'],
                    name=row['name'],
                    category=row['category'],
                    email=row['email'],
                    phone=row['phone'],
                    photo_url=row['photo_url'],
                    created_at=parse_snapshot_datetime(row['created_at']) or datetime.utcnow(),
                )
            )

        for row in product_rows:
            row_keys = set(row.keys())
            availability_status = row['availability_status'] if 'availability_status' in row_keys else 'Open'
            if availability_status not in PRODUCT_STATUS_OPTIONS:
                availability_status = 'Open'
            db.session.merge(
                Product(
                    id=row['id'],
                    title=row['title'],
                    category=row['category'],
                    domain=row['domain'],
                    availability_status=availability_status,
                    image_url=row['image_url'] if 'image_url' in row_keys else None,
                    description=row['description'],
                    procedure=row['procedure'],
                    achievements=row['achievements'],
                    price=row['price'],
                    created_at=parse_snapshot_datetime(row['created_at']) or datetime.utcnow(),
                )
            )

        for row in purchase_rows:
            db.session.merge(
                Purchase(
                    id=row['id'],
                    user_id=row['user_id'],
                    product_id=row['product_id'],
                    status=row['status'] or 'Active',
                    created_at=parse_snapshot_datetime(row['created_at']) or datetime.utcnow(),
                )
            )

        for row in submission_rows:
            db.session.merge(
                Submission(
                    id=row['id'],
                    user_id=row['user_id'],
                    product_id=row['product_id'],
                    github_link=row['github_link'],
                    created_at=parse_snapshot_datetime(row['created_at']) or datetime.utcnow(),
                )
            )

        for row in certificate_rows:
            db.session.merge(
                Certificate(
                    id=row['id'],
                    cert_code=row['cert_code'],
                    user_id=row['user_id'],
                    product_id=row['product_id'],
                    created_at=parse_snapshot_datetime(row['created_at']) or datetime.utcnow(),
                )
            )

        db.session.commit()
    finally:
        source_connection.close()


with app.app_context():
    db.create_all()
    ensure_database_schema()
    seed_database_from_local_snapshot()


def get_site_content_map():
    content = DEFAULT_SITE_CONTENT.copy()
    for item in SiteContent.query.all():
        content[item.key] = item.value
    return content


def normalize_product_status(value):
    cleaned = (value or '').strip()
    if cleaned in PRODUCT_STATUS_OPTIONS:
        return cleaned
    return 'Open'


def get_status_label(status):
    mapping = {
        'Open': 'Currently Open',
        'Closed': 'Currently Closed',
        'Coming Soon': 'Coming Soon',
    }
    return mapping.get(status, 'Currently Open')


def get_status_class(status):
    mapping = {
        'Open': 'status-open',
        'Closed': 'status-closed',
        'Coming Soon': 'status-coming-soon',
    }
    return mapping.get(status, 'status-open')


def is_allowed_image(filename):
    if '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in ALLOWED_IMAGE_EXTENSIONS


def save_uploaded_file(file_storage, prefix):
    if not file_storage or not file_storage.filename:
        return None

    if not is_allowed_image(file_storage.filename):
        return None

    extension = file_storage.filename.rsplit('.', 1)[1].lower()
    filename = secure_filename(
        f"{prefix}-{uuid.uuid4().hex[:12]}.{extension}"
    )
    destination = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file_storage.save(destination)
    return f"/uploads/{filename}"


def get_submitted_content_value(key, form_data, files):
    field = SITE_FIELD_MAP.get(key, {})
    upload_name = field.get('upload_name')
    if upload_name:
        uploaded_path = save_uploaded_file(
            files.get(upload_name),
            key.replace('_', '-'),
        )
        if uploaded_path:
            return uploaded_path
    return (form_data.get(key) or '').strip()


def save_site_content(form_data, files):
    existing_items = {item.key: item for item in SiteContent.query.all()}
    for key in DEFAULT_SITE_CONTENT:
        value = get_submitted_content_value(key, form_data, files)
        if key in existing_items:
            existing_items[key].value = value
        else:
            db.session.add(SiteContent(key=key, value=value))
    db.session.commit()


def get_category_fallback_image(category, content=None):
    content = content or get_site_content_map()
    mapping = {
        'Internship': content['default_internship_image'],
        'Project': content['default_project_image'],
        'Task': content['default_task_image'],
    }
    return mapping.get(category, content['default_project_image'])


def resolve_product_image(product, content=None):
    content = content or get_site_content_map()
    if product and product.image_url:
        return product.image_url
    return get_category_fallback_image(product.category if product else '', content)


def build_domain_defaults(domain_name):
    return {
        'badge': DEFAULT_SITE_CONTENT['domain_badge'],
        'headline': domain_name,
        'description': DEFAULT_SITE_CONTENT['domain_default_description'].replace('this domain', domain_name),
    }


def sync_domain_records():
    product_domain_names = {
        product.domain.strip()
        for product in Product.query.all()
        if product.domain
    }
    existing_names = {domain.name for domain in DomainContent.query.all()}
    created = False

    for domain_name in sorted(product_domain_names - existing_names):
        defaults = build_domain_defaults(domain_name)
        db.session.add(
            DomainContent(
                name=domain_name,
                badge=defaults['badge'],
                headline=defaults['headline'],
                description=defaults['description'],
            )
        )
        created = True

    if created:
        db.session.commit()


def get_all_domain_names():
    sync_domain_records()
    domain_names = {
        domain.name for domain in DomainContent.query.all() if domain.name
    }
    domain_names.update(
        product.domain.strip() for product in Product.query.all() if product.domain
    )
    return sorted(domain_names)


def admin_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Please log in to access the admin panel.')
            return redirect(url_for('admin_login'))
        return view_func(*args, **kwargs)

    return wrapped_view


def parse_price(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def upsert_domain_by_name(domain_name):
    clean_name = (domain_name or '').strip()
    if not clean_name:
        return None

    domain = DomainContent.query.filter_by(name=clean_name).first()
    if domain:
        return domain

    defaults = build_domain_defaults(clean_name)
    domain = DomainContent(
        name=clean_name,
        badge=defaults['badge'],
        headline=defaults['headline'],
        description=defaults['description'],
    )
    db.session.add(domain)
    db.session.flush()
    return domain


@app.context_processor
def inject_shared_context():
    content = get_site_content_map()
    return {
        'site_content': content,
        'admin_logged_in': session.get('is_admin', False),
        'current_year': datetime.utcnow().year,
        'is_render_runtime': os.environ.get('RENDER') == 'true',
        'is_database_backed': bool(os.environ.get('DATABASE_URL')),
        'admin_url_prefix': app.config['ADMIN_URL_PREFIX'],
        'product_image_for': lambda product: resolve_product_image(product, content),
        'product_status_label': get_status_label,
        'product_status_class': get_status_class,
        'product_status_options': PRODUCT_STATUS_OPTIONS,
    }


@app.route('/')
def index():
    products = Product.query.order_by(Product.created_at.desc(), Product.id.desc()).all()
    domains = get_all_domain_names()
    internships = [product for product in products if product.category == 'Internship']
    projects = [product for product in products if product.category == 'Project']
    tasks = [product for product in products if product.category == 'Task']
    return render_template(
        'index.html',
        internships=internships,
        projects=projects,
        tasks=tasks,
        domains=domains,
    )


@app.route('/domain/<string:domain_name>')
def domain_page(domain_name):
    sync_domain_records()
    domain_content = DomainContent.query.filter_by(name=domain_name).first()
    products = Product.query.filter_by(domain=domain_name).all()

    if not products and not domain_content:
        flash('Domain not found or has no products.')
        return redirect(url_for('index'))

    internships = [product for product in products if product.category == 'Internship']
    projects = [product for product in products if product.category == 'Project']
    tasks = [product for product in products if product.category == 'Task']
    featured_products = []
    seen_product_ids = set()
    for group in (internships, projects, tasks):
        if group:
            featured_products.append(group[0])
            seen_product_ids.add(group[0].id)

    for product in products:
        if product.id not in seen_product_ids and len(featured_products) < 3:
            featured_products.append(product)
            seen_product_ids.add(product.id)

    status_counts = {
        'Open': sum(1 for product in products if normalize_product_status(product.availability_status) == 'Open'),
        'Closed': sum(1 for product in products if normalize_product_status(product.availability_status) == 'Closed'),
        'Coming Soon': sum(1 for product in products if normalize_product_status(product.availability_status) == 'Coming Soon'),
    }
    return render_template(
        'domain.html',
        domain_name=domain_name,
        domain_content=domain_content,
        internships=internships,
        projects=projects,
        tasks=tasks,
        featured_products=featured_products,
        status_counts=status_counts,
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        unique_code = request.form.get('unique_code')
        user = User.query.filter_by(unique_code=unique_code).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        flash('Invalid Code')
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = db.session.get(User, session['user_id'])
    if not user:
        session.pop('user_id', None)
        flash('Please log in again.')
        return redirect(url_for('login'))

    purchases = Purchase.query.filter_by(user_id=user.id).order_by(Purchase.id.desc()).all()
    return render_template('dashboard.html', user=user, purchases=purchases)


@app.route('/submit/<int:purchase_id>', methods=['POST'])
def submit_task(purchase_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    purchase = Purchase.query.get_or_404(purchase_id)
    if purchase.user_id != session['user_id']:
        flash('Unauthorized')
        return redirect(url_for('dashboard'))

    github_link = request.form.get('github_link')
    if github_link:
        purchase.status = 'Completed'
        submission = Submission(
            user_id=purchase.user_id,
            product_id=purchase.product_id,
            github_link=github_link,
        )
        db.session.add(submission)

        cert = Certificate.query.filter_by(
            user_id=purchase.user_id,
            product_id=purchase.product_id,
        ).first()
        if not cert:
            cert_code = f"CERT-BRIT-{str(uuid.uuid4())[:8].upper()}"
            cert = Certificate(
                cert_code=cert_code,
                user_id=purchase.user_id,
                product_id=purchase.product_id,
            )
            db.session.add(cert)

        db.session.commit()
        return redirect(url_for('view_certificate', cert_code=cert.cert_code))

    flash('Please provide a valid GitHub link.')
    return redirect(url_for('dashboard'))


@app.route('/details/<int:product_id>')
def details(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('details.html', product=product)


@app.route(f"{app.config['ADMIN_URL_PREFIX']}/login", methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''
        if (
            username == app.config['ADMIN_USERNAME']
            and password == app.config['ADMIN_PASSWORD']
        ):
            session['is_admin'] = True
            session['admin_username'] = username
            flash('Welcome to the admin panel.')
            return redirect(url_for('admin_dashboard'))
        flash('Invalid admin username or password.')
    return render_template('admin_login.html')


@app.route(f"{app.config['ADMIN_URL_PREFIX']}/logout")
@admin_required
def admin_logout():
    session.pop('is_admin', None)
    session.pop('admin_username', None)
    flash('You have been logged out from the admin panel.')
    return redirect(url_for('admin_login'))


@app.route(app.config['ADMIN_URL_PREFIX'])
@admin_required
def admin_dashboard():
    sync_domain_records()
    products = Product.query.order_by(Product.id.desc()).all()
    domains = DomainContent.query.order_by(DomainContent.name.asc()).all()
    users = User.query.order_by(User.created_at.desc()).all()
    content_map = get_site_content_map()
    domain_product_counts = {
        domain.name: Product.query.filter_by(domain=domain.name).count()
        for domain in domains
    }
    product_counts = {
        'Internship': Product.query.filter_by(category='Internship').count(),
        'Project': Product.query.filter_by(category='Project').count(),
        'Task': Product.query.filter_by(category='Task').count(),
    }
    return render_template(
        'admin.html',
        products=products,
        domains=domains,
        users=users,
        product_counts=product_counts,
        domain_product_counts=domain_product_counts,
        content_map=content_map,
        content_sections=CONTENT_SECTIONS,
        domain_names=get_all_domain_names(),
    )


@app.route(f"{app.config['ADMIN_URL_PREFIX']}/content", methods=['POST'])
@admin_required
def update_site_content():
    save_site_content(request.form, request.files)
    flash('Website content, images, and styling updated successfully.')
    return redirect(url_for('admin_dashboard') + '#content-panel')


@app.route(f"{app.config['ADMIN_URL_PREFIX']}/domains", methods=['POST'])
@admin_required
def create_domain():
    name = (request.form.get('name') or '').strip()
    if not name:
        flash('Domain name is required.')
        return redirect(url_for('admin_dashboard') + '#domain-panel')

    if DomainContent.query.filter_by(name=name).first():
        flash('That domain already exists.')
        return redirect(url_for('admin_dashboard') + '#domain-panel')

    domain = DomainContent(
        name=name,
        badge=(request.form.get('badge') or DEFAULT_SITE_CONTENT['domain_badge']).strip(),
        headline=(request.form.get('headline') or name).strip(),
        description=(request.form.get('description') or '').strip(),
    )
    db.session.add(domain)
    db.session.commit()
    flash('Domain added successfully.')
    return redirect(url_for('admin_dashboard') + '#domain-panel')


@app.route(f"{app.config['ADMIN_URL_PREFIX']}/domains/<int:domain_id>/edit", methods=['POST'])
@admin_required
def update_domain(domain_id):
    domain = DomainContent.query.get_or_404(domain_id)
    old_name = domain.name
    new_name = (request.form.get('name') or '').strip()

    if not new_name:
        flash('Domain name is required.')
        return redirect(url_for('admin_dashboard') + '#domain-panel')

    duplicate = DomainContent.query.filter(
        DomainContent.name == new_name,
        DomainContent.id != domain_id,
    ).first()
    if duplicate:
        flash('Another domain already uses that name.')
        return redirect(url_for('admin_dashboard') + '#domain-panel')

    domain.name = new_name
    domain.badge = (request.form.get('badge') or DEFAULT_SITE_CONTENT['domain_badge']).strip()
    domain.headline = (request.form.get('headline') or new_name).strip()
    domain.description = (request.form.get('description') or '').strip()

    if old_name != new_name:
        for product in Product.query.filter_by(domain=old_name).all():
            product.domain = new_name

    db.session.commit()
    flash('Domain updated successfully.')
    return redirect(url_for('admin_dashboard') + '#domain-panel')


@app.route(f"{app.config['ADMIN_URL_PREFIX']}/domains/<int:domain_id>/delete", methods=['POST'])
@admin_required
def delete_domain(domain_id):
    domain = DomainContent.query.get_or_404(domain_id)
    linked_products = Product.query.filter_by(domain=domain.name).count()
    if linked_products:
        flash('Move or delete the products in this domain before removing it.')
        return redirect(url_for('admin_dashboard') + '#domain-panel')

    db.session.delete(domain)
    db.session.commit()
    flash('Domain deleted successfully.')
    return redirect(url_for('admin_dashboard') + '#domain-panel')


@app.route(f"{app.config['ADMIN_URL_PREFIX']}/products", methods=['POST'])
@admin_required
def create_product():
    title = (request.form.get('title') or '').strip()
    category = (request.form.get('category') or '').strip()
    domain_name = (request.form.get('domain') or '').strip()
    availability_status = normalize_product_status(request.form.get('availability_status'))
    description = (request.form.get('description') or '').strip()
    price = parse_price(request.form.get('price'))

    if not all([title, category, domain_name, description]) or price is None:
        flash('Please fill in all required product fields with a valid price.')
        return redirect(url_for('admin_dashboard') + '#product-panel')

    image_url = (request.form.get('image_url') or '').strip()
    uploaded_image = save_uploaded_file(
        request.files.get('image_file'),
        'product',
    )
    if uploaded_image:
        image_url = uploaded_image

    upsert_domain_by_name(domain_name)
    product = Product(
        title=title,
        category=category,
        domain=domain_name,
        availability_status=availability_status,
        image_url=image_url,
        price=price,
        description=description,
        procedure=(request.form.get('procedure') or '').strip(),
        achievements=(request.form.get('achievements') or '').strip(),
    )
    db.session.add(product)
    db.session.commit()
    flash('Product added successfully.')
    return redirect(url_for('admin_dashboard') + '#product-panel')


@app.route(f"{app.config['ADMIN_URL_PREFIX']}/products/<int:product_id>/edit", methods=['POST'])
@admin_required
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    title = (request.form.get('title') or '').strip()
    category = (request.form.get('category') or '').strip()
    domain_name = (request.form.get('domain') or '').strip()
    availability_status = normalize_product_status(request.form.get('availability_status'))
    description = (request.form.get('description') or '').strip()
    price = parse_price(request.form.get('price'))

    if not all([title, category, domain_name, description]) or price is None:
        flash('Please fill in all required product fields with a valid price.')
        return redirect(url_for('admin_dashboard') + '#product-panel')

    image_url = (request.form.get('image_url') or '').strip()
    uploaded_image = save_uploaded_file(
        request.files.get('image_file'),
        'product',
    )
    if uploaded_image:
        image_url = uploaded_image

    upsert_domain_by_name(domain_name)
    product.title = title
    product.category = category
    product.domain = domain_name
    product.availability_status = availability_status
    product.image_url = image_url
    product.price = price
    product.description = description
    product.procedure = (request.form.get('procedure') or '').strip()
    product.achievements = (request.form.get('achievements') or '').strip()
    db.session.commit()
    flash('Product updated successfully.')
    return redirect(url_for('admin_dashboard') + '#product-panel')


@app.route(f"{app.config['ADMIN_URL_PREFIX']}/products/<int:product_id>/delete", methods=['POST'])
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully.')
    return redirect(url_for('admin_dashboard') + '#product-panel')


@app.route('/health')
def health():
    return {'status': 'ok'}, 200


@app.route('/verification')
def verification():
    cert_code = request.args.get('cert_code')
    certificate = None
    if cert_code:
        cert_code = cert_code.strip()
        certificate = Certificate.query.filter_by(cert_code=cert_code).first()
    return render_template('verification.html', certificate=certificate, cert_code=cert_code)


@app.route('/certificate/<cert_code>')
def view_certificate(cert_code):
    certificate = Certificate.query.filter_by(cert_code=cert_code).first_or_404()
    return render_template('certificate.html', certificate=certificate)


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
