import os
import random
from datetime import datetime, timedelta
from app.models.models import db, User, Product, Activity, Notification, Transaction


def init_db(app):
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'database', 'admin.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    db.create_all()

    if User.query.count() == 0:
        _seed_data()


def _seed_data():
    admin = User(
        username='admin',
        email='admin@admin.com',
        role='admin',
        status='active',
        bio='Platform administrator',
        theme='dark'
    )
    admin.set_password('admin123')
    db.session.add(admin)

    sample_users = []
    user_data = [
        ('john_doe', 'john@example.com', 'user', 'active', 'Software developer'),
        ('jane_smith', 'jane@example.com', 'user', 'active', 'Product manager'),
        ('bob_wilson', 'bob@example.com', 'user', 'active', 'Designer'),
        ('alice_brown', 'alice@example.com', 'moderator', 'active', 'Content moderator'),
        ('charlie_davis', 'charlie@example.com', 'user', 'inactive', 'Data analyst'),
        ('diana_evans', 'diana@example.com', 'user', 'active', 'Marketing lead'),
        ('frank_garcia', 'frank@example.com', 'user', 'active', 'Sales rep'),
        ('grace_harris', 'grace@example.com', 'moderator', 'active', 'Community manager'),
        ('henry_irwin', 'henry@example.com', 'user', 'suspended', 'Freelancer'),
        ('isla_johnson', 'isla@example.com', 'user', 'active', 'UX researcher'),
        ('jack_king', 'jack@example.com', 'user', 'active', 'Backend dev'),
        ('kate_lee', 'kate@example.com', 'user', 'active', 'Frontend dev'),
    ]
    for uname, uemail, urole, ustatus, ubio in user_data:
        u = User(username=uname, email=uemail, role=urole, status=ustatus, bio=ubio)
        u.set_password('password123')
        db.session.add(u)
        sample_users.append(u)

    products = []
    product_data = [
        ('Wireless Headphones', 'Premium noise-cancelling wireless headphones', 149.99, 'Electronics', 45),
        ('Smart Watch', 'Fitness tracking smartwatch with GPS', 199.99, 'Electronics', 30),
        ('Leather Notebook', 'Handcrafted leather-bound notebook', 24.99, 'Stationery', 120),
        ('Ergonomic Keyboard', 'Mechanical keyboard with ergonomic design', 89.99, 'Electronics', 60),
        ('Desk Lamp', 'LED desk lamp with adjustable brightness', 39.99, 'Furniture', 80),
        ('Coffee Mug', 'Ceramic mug with heat-changing design', 14.99, 'Kitchen', 200),
        ('Backpack', 'Waterproof laptop backpack 40L', 59.99, 'Accessories', 75),
        ('Plant Pot Set', 'Set of 3 minimalist plant pots', 29.99, 'Home', 90),
        ('USB-C Hub', '7-in-1 USB-C hub with 4K HDMI', 44.99, 'Electronics', 55),
        ('Yoga Mat', 'Premium non-slip yoga mat 6mm', 34.99, 'Sports', 65),
        ('Bluetooth Speaker', 'Portable waterproof speaker', 79.99, 'Electronics', 40),
        ('Sunglasses', 'Polarized UV400 protection sunglasses', 54.99, 'Accessories', 100),
    ]
    for pname, pdesc, pprice, pcat, pstock in product_data:
        p = Product(name=pname, description=pdesc, price=pprice, category=pcat, stock=pstock)
        db.session.add(p)
        products.append(p)

    db.session.flush()

    activities = [
        ('User login', 'admin logged in from Chrome on Windows'),
        ('New user registered', 'john_doe created an account'),
        ('Product added', 'Wireless Headphones added to inventory'),
        ('Sale completed', 'Order #1024 processed successfully'),
        ('Report generated', 'Monthly sales report exported'),
        ('Settings updated', 'System configuration changed'),
        ('Password changed', 'User jane_smith updated password'),
        ('Product updated', 'Smart Watch price changed to $199.99'),
        ('New user registered', 'bob_wilson created an account'),
        ('Backup completed', 'Database backup finished successfully'),
        ('Transaction processed', 'Payment of $149.99 received'),
        ('User profile updated', 'alice_brown updated profile picture'),
    ]
    for action, details in activities:
        a = Activity(user_id=random.choice([admin.id] + [u.id for u in sample_users]),
                     action=action, details=details,
                     created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 72)))
        db.session.add(a)

    notifications = [
        ('New Sale!', 'Order #1024 for $149.99 has been completed.', 'success'),
        ('Welcome', 'Welcome to the Admin Dashboard!', 'info'),
        ('Security Alert', 'New login detected from unknown device.', 'warning'),
        ('Update Available', 'Version 2.5.0 is ready for installation.', 'info'),
        ('Low Stock', 'Leather Notebook is running low on stock.', 'danger'),
        ('Report Ready', 'Q2 Financial Report is ready for review.', 'info'),
    ]
    for title, message, ntype in notifications:
        n = Notification(user_id=admin.id, title=title, message=message, type=ntype,
                         created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 48)))
        db.session.add(n)

    transactions = [
        (admin.id, products[0].id, 149.99, 'completed'),
        (sample_users[0].id, products[2].id, 24.99, 'completed'),
        (sample_users[1].id, products[1].id, 199.99, 'completed'),
        (sample_users[2].id, products[3].id, 89.99, 'pending'),
        (sample_users[3].id, products[4].id, 39.99, 'completed'),
        (admin.id, products[5].id, 14.99, 'completed'),
        (sample_users[4].id, products[6].id, 59.99, 'completed'),
        (sample_users[5].id, products[7].id, 29.99, 'refunded'),
        (sample_users[6].id, products[8].id, 44.99, 'completed'),
        (sample_users[0].id, products[9].id, 34.99, 'completed'),
        (sample_users[1].id, products[10].id, 79.99, 'pending'),
        (sample_users[2].id, products[11].id, 54.99, 'completed'),
    ]
    for uid, pid, amount, status in transactions:
        t = Transaction(user_id=uid, product_id=pid, amount=amount, status=status,
                        created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)))
        db.session.add(t)

    db.session.commit()
