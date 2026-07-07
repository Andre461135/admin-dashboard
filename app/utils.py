import os
import random
import string
from datetime import datetime, timedelta, timezone
from werkzeug.utils import secure_filename
from faker import Faker
from app import db
from app.models import User, Product, Activity, Notification, Sale

fake = Faker()


def save_file(file, upload_folder):
    if not file:
        return None
    filename = secure_filename(file.filename)
    if not filename:
        return None
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    if ext not in {'png', 'jpg', 'jpeg', 'gif', 'svg'}:
        return None
    new_filename = f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{random.randint(1000,9999)}.{ext}"
    file.save(os.path.join(upload_folder, new_filename))
    return new_filename


def log_activity(user_id, action, details=None, entity_type=None, entity_id=None):
    activity = Activity(
        user_id=user_id,
        action=action,
        details=details,
        entity_type=entity_type,
        entity_id=entity_id
    )
    db.session.add(activity)
    db.session.commit()


def create_notification(user_id, title, message, type='info'):
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=type
    )
    db.session.add(notification)
    db.session.commit()


def seed_database(app):
    if User.query.first() is not None:
        return

    print("Seeding database with sample data...")

    admin = User(
        username='admin',
        email='admin@dashboard.com',
        full_name='Admin User',
        role='admin',
        status='active',
        bio='Platform administrator',
        phone='+1-555-0100',
        theme='light',
        notifications_enabled=True
    )
    admin.set_password('admin123')
    db.session.add(admin)

    demo = User(
        username='demo',
        email='demo@dashboard.com',
        full_name='Demo User',
        role='user',
        status='active',
        bio='Demo account user',
        phone='+1-555-0101',
        theme='dark',
        notifications_enabled=True
    )
    demo.set_password('demo123')
    db.session.add(demo)
    db.session.commit()

    roles = ['user', 'user', 'user', 'editor', 'editor', 'admin']
    statuses = ['active', 'active', 'active', 'active', 'inactive', 'suspended']
    users = [admin, demo]

    for i in range(18):
        user = User(
            username=fake.user_name() + str(random.randint(10, 99)),
            email=fake.email(),
            full_name=fake.name(),
            role=random.choice(roles),
            status=random.choice(statuses),
            bio=fake.text(max_nb_chars=100),
            phone=fake.phone_number()[:20],
            theme=random.choice(['light', 'dark']),
            notifications_enabled=random.choice([True, False]),
            email_notifications=random.choice([True, False]),
            created_at=fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.utc)
        )
        user.set_password('password123')
        users.append(user)
        db.session.add(user)

    db.session.commit()

    categories = ['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports', 'Food', 'Software', 'Accessories']
    status_opts = ['active', 'active', 'active', 'active', 'inactive', 'discontinued']
    all_products = []

    product_names = [
        'Wireless Headphones', 'Smart Watch Pro', 'Organic Cotton T-Shirt', 'Designer Desk Lamp',
        'Python Programming Guide', 'Yoga Mat Premium', 'Bluetooth Speaker', 'Leather Wallet',
        'Running Shoes Ultra', 'Coffee Maker Deluxe', 'USB-C Hub 7-in-1', 'Sunglasses Aviator',
        'Backpack Explorer', 'Mechanical Keyboard', 'Portable Charger 20000mAh', 'Noise Cancelling Earbuds',
        'Fitness Tracker Band', 'Canvas Backpack', 'Desk Organizer', 'Water Bottle Insulated',
        'LED Strip Lights', 'Phone Stand Adjustable', 'Memory Foam Pillow', 'Stainless Steel Water Bottle'
    ]

    for i, name in enumerate(product_names):
        product = Product(
            name=name,
            description=fake.text(max_nb_chars=150),
            price=round(random.uniform(9.99, 499.99), 2),
            category=random.choice(categories),
            stock=random.randint(0, 200),
            sku=f"SKU-{random.randint(10000, 99999)}",
            status=random.choice(status_opts),
            user_id=random.choice(users).id,
            created_at=fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.utc)
        )
        all_products.append(product)
        db.session.add(product)

    db.session.commit()

    actions = [
        'User logged in', 'New user registered', 'Product created', 'Product updated',
        'Order placed', 'Order completed', 'Profile updated', 'Password changed',
        'Report generated', 'Settings updated', 'Product deleted', 'User deleted',
        'Bulk import completed', 'Export initiated', 'Payment received'
    ]

    for i in range(50):
        user = random.choice(users)
        activity = Activity(
            user_id=user.id,
            action=random.choice(actions),
            details=fake.sentence(),
            entity_type=random.choice(['user', 'product', 'order', 'report']),
            entity_id=random.randint(1, 100),
            created_at=fake.date_time_between(start_date='-30d', end_date='now', tzinfo=timezone.utc)
        )
        db.session.add(activity)

    db.session.commit()

    notification_templates = [
        ('New user registered', 'A new user has joined the platform.', 'info'),
        ('Payment received', 'Payment of $499.99 has been received.', 'success'),
        ('System update', 'System maintenance scheduled for tonight.', 'warning'),
        ('New order', 'You have received a new order.', 'info'),
        ('Low stock alert', 'Product "Wireless Headphones" is low on stock.', 'warning'),
        ('Account updated', 'Your profile has been updated successfully.', 'success'),
        ('Security alert', 'New login detected from an unknown device.', 'danger'),
        ('Report ready', 'Monthly sales report is ready for download.', 'info'),
    ]

    for i in range(15):
        user = random.choice(users)
        title, message, ntype = random.choice(notification_templates)
        notification = Notification(
            user_id=user.id,
            title=title,
            message=message,
            type=ntype,
            is_read=random.choice([True, False, False]),
            created_at=fake.date_time_between(start_date='-7d', end_date='now', tzinfo=timezone.utc)
        )
        db.session.add(notification)

    db.session.commit()

    for i in range(30):
        product = random.choice(all_products)
        buyer = random.choice(users)
        qty = random.randint(1, 5)
        sale = Sale(
            product_id=product.id,
            user_id=buyer.id,
            quantity=qty,
            total=round(product.price * qty, 2),
            status=random.choice(['completed', 'completed', 'completed', 'pending', 'cancelled']),
            created_at=fake.date_time_between(start_date='-60d', end_date='now', tzinfo=timezone.utc)
        )
        db.session.add(sale)

    db.session.commit()
    print("Database seeded successfully!")
