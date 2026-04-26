from app import app, db
from models import DomainContent, Product, User, Purchase, Certificate
import random

with app.app_context():
    db.drop_all()
    db.create_all()

    domains = [
        "Web Development", "Health Administration", "Data Science", "UX/UI Design",
        "Cyber Security", "Cloud Computing", "Artificial Intelligence", "Digital Marketing",
        "Finance & Accounting", "Human Resources", "Project Management", "Business Analytics",
        "Mobile App Development", "Blockchain", "Internet of Things", "Sales & Negotiation",
        "Supply Chain", "Content Creation", "Graphic Design", "Software Testing",
        "DevOps Engineering", "Game Development", "Network Engineering", "E-commerce Management",
        "Customer Success"
    ]

    categories = ["Internship", "Project", "Task"]
    products = []

    # Generate 50+ products across the 25 domains
    for domain in domains:
        db.session.add(DomainContent(
            name=domain,
            badge="DOMAIN OVERVIEW",
            headline=domain,
            description=f"Master the required skills for {domain} through our structured programs below."
        ))
        # 1 Internship per domain
        products.append(Product(
            title=f"{domain} Mastery Internship",
            category="Internship",
            domain=domain,
            availability_status="Open",
            description=f"A deep, comprehensive 90-day internship covering core concepts of {domain}. Gain hands-on experience and build real-world applications.",
            procedure="1. Make Payment 2. Register Account 3. Start tasks via Dashboard 4. Submit GitHub links",
            achievements="Certificate of Internship, 3 Live Projects, Letter of Recommendation",
            price=299.00
        ))
        # 1 Project per domain
        products.append(Product(
            title=f"Advanced {domain} Project",
            category="Project",
            domain=domain,
            availability_status="Open",
            description=f"Complete an industry-level project in {domain}. You will work through 3 tiers of difficulty to build a stunning portfolio piece.",
            procedure="Purchase, build, submit github link, get reviewed.",
            achievements="Project completion certificate, Portfolio piece",
            price=49.00
        ))
        # 1 Task per domain
        products.append(Product(
            title=f"Essential {domain} Task",
            category="Task",
            domain=domain,
            availability_status="Open",
            description=f"A focused 7-day sprint to master a specific skill within {domain}.",
            procedure="Purchase, complete in 7 days, submit code.",
            achievements="Task completion badge",
            price=15.00
        ))

    db.session.add_all(products)
    
    # Add a sample user
    u1 = User(
        unique_code="TEST-CODE-123",
        name="John Doe",
        category="Web Development",
        email="john@example.com"
    )
    db.session.add(u1)
    db.session.commit()

    # Add sample purchase
    purchase = Purchase(user_id=u1.id, product_id=products[0].id, status="Active")
    db.session.add(purchase)
    
    # Add sample certificate
    cert = Certificate(cert_code="CERT-BRIT-2026", user_id=u1.id, product_id=products[0].id)
    db.session.add(cert)
    
    db.session.commit()
    print("Database initialized with 25 domains and 75 products.")
