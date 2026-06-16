"""
Seed script to populate KasbLink with realistic demo data.
Run via: uv run python manage.py shell < seed_data.py
"""
import os
import urllib
from tempfile import NamedTemporaryFile

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "root.settings")

import django
django.setup()

from datetime import datetime, timezone  # noqa: E402
from decimal import Decimal  # noqa: E402
from django.core.files import File  # noqa: E402
from apps.models import User, WorkerProfile, Category, Service, Order, Conversation, Message, Review, Portfolio  # noqa: E402
from apps.models.users import District  # noqa: E402

print("=== Seeding KasbLink Demo Data ===\n")

# --- Categories ---
cats = {}
for name, slug in [
    ("Plumbing", "plumbing"),
    ("Electrical", "electrical"),
    ("Cleaning", "cleaning"),
    ("Painting", "painting"),
    ("Carpentry", "carpentry"),
]:
    cat, _ = Category.objects.get_or_create(name=name, slug=slug)
    cats[name] = cat
    print(f"  Category: {name}")

# --- Worker Users ---
workers_data = [
    {
        "username": "farid_master",
        "first_name": "Farid",
        "last_name": "Karimov",
        "phone_number": "901234501",
        "bio": "10+ years experience in plumbing. Fast, reliable, and affordable service for kitchens and bathrooms.",
        "start": "08:00",
        "end": "18:00",
        "rating": Decimal("4.8"),
        "completed": 47,
        "services": [
            ("Kitchen Faucet Repair", "Complete faucet replacement and leak repair for all kitchen types.", "Plumbing", 50000, 150000),
            ("Bathroom Pipe Installation", "New pipe installation and old pipe replacement for bathrooms.", "Plumbing", 80000, 250000),
        ]
    },
    {
        "username": "aziz_electric",
        "first_name": "Aziz",
        "last_name": "Rakhimov",
        "phone_number": "901234502",
        "bio": "Certified electrician specializing in home wiring, smart lighting, and circuit repairs.",
        "start": "09:00",
        "end": "19:00",
        "rating": Decimal("4.6"),
        "completed": 32,
        "services": [
            ("Home Wiring Inspection", "Full electrical inspection of your home wiring with detailed report.", "Electrical", 100000, 200000),
            ("Light Fixture Installation", "Install any type of ceiling or wall-mounted light fixtures.", "Electrical", 30000, 80000),
            ("Smart Switch Setup", "Configure and install smart switches and dimmers for home automation.", "Electrical", 60000, 120000),
        ]
    },
    {
        "username": "malika_clean",
        "first_name": "Malika",
        "last_name": "Saidova",
        "phone_number": "901234503",
        "bio": "Professional deep cleaning services. Eco-friendly products and attention to every detail.",
        "start": "07:00",
        "end": "17:00",
        "rating": Decimal("4.9"),
        "completed": 63,
        "services": [
            ("Deep Home Cleaning", "Full apartment deep cleaning including kitchen, bathrooms, and living areas.", "Cleaning", 150000, 350000),
            ("Office Cleaning", "Professional office cleaning with sanitization. Weekends available.", "Cleaning", 200000, 500000),
        ]
    },
    {
        "username": "rustam_painter",
        "first_name": "Rustam",
        "last_name": "Nazarov",
        "phone_number": "901234504",
        "bio": "Interior and exterior painting specialist. Free color consultation included.",
        "start": "08:00",
        "end": "20:00",
        "rating": Decimal("4.5"),
        "completed": 28,
        "services": [
            ("Interior Wall Painting", "Professional wall painting with premium paint. Includes surface preparation.", "Painting", 120000, 400000),
            ("Ceiling Whitewash", "Clean ceiling whitewash and minor crack repair.", "Painting", 80000, 180000),
        ]
    },
    {
        "username": "bobur_wood",
        "first_name": "Bobur",
        "last_name": "Toshmatov",
        "phone_number": "901234505",
        "bio": "Custom furniture maker and wood repair expert. From shelves to full kitchen cabinets.",
        "start": "09:00",
        "end": "18:00",
        "rating": Decimal("4.7"),
        "completed": 41,
        "services": [
            ("Custom Shelf Building", "Build custom wooden shelves to your exact specifications.", "Carpentry", 100000, 300000),
            ("Door Repair & Installation", "Repair damaged doors or install new interior/exterior doors.", "Carpentry", 80000, 250000),
            ("Kitchen Cabinet Refacing", "Give your kitchen a new look with cabinet door replacement.", "Carpentry", 200000, 600000),
        ]
    },
]

worker_profiles = {}
all_services = []

for wd in workers_data:
    user, created = User.objects.get_or_create(
        username=wd["username"],
        defaults={
            "first_name": wd["first_name"],
            "last_name": wd["last_name"],
            "phone_number": wd["phone_number"],
            "role": "worker",
        }
    )
    if created:
        user.set_password("Demo1234!")
        user.save()
    print(f"  Worker: {user.first_name} {user.last_name} (@{user.username})")

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    wp, _ = WorkerProfile.objects.get_or_create(
        user=user,
        defaults={
            "bio": wd["bio"],
            "work_start_time": f"{today}T{wd['start']}:00Z",
            "work_end_time": f"{today}T{wd['end']}:00Z",
            "rating": wd["rating"],
            "completed_orders_count": wd["completed"],
            "is_available": True,
        }
    )
    worker_profiles[wd["username"]] = wp
    
    # Assign some districts
    districts = list(District.objects.order_by('?')[:3])
    if districts:
        wp.service_districts.set(districts)

    for sname, sdesc, scat, smin, smax in wd["services"]:
        svc, _ = Service.objects.get_or_create(
            name=sname,
            worker=wp,
            defaults={
                "description": sdesc,
                "category": cats[scat],
                "min_price": smin,
                "max_price": smax,
                "active": True,
            }
        )
        all_services.append(svc)
        print(f"    Service: {sname} ({smin:,}-{smax:,} UZS)")

# --- Client Users ---
clients_data = [
    {"username": "sardor_client", "first_name": "Sardor", "last_name": "Umarov", "phone_number": "901234510"},
    {"username": "nodira_client", "first_name": "Nodira", "last_name": "Abdullaeva", "phone_number": "901234511"},
    {"username": "jamshid_client", "first_name": "Jamshid", "last_name": "Khodjaev", "phone_number": "901234512"},
]

client_users = []
for cd in clients_data:
    user, created = User.objects.get_or_create(
        username=cd["username"],
        defaults={
            "first_name": cd["first_name"],
            "last_name": cd["last_name"],
            "phone_number": cd["phone_number"],
            "role": "customer",
        }
    )
    if created:
        user.set_password("Demo1234!")
        user.save()
    client_users.append(user)
    print(f"  Client: {user.first_name} {user.last_name} (@{user.username})")


# --- Orders ---
print("\n--- Creating Orders ---")
orders_data = [
    # (client_idx, worker_username, service_idx_in_worker, title, desc, address, status)
    (0, "farid_master", 0, "Kitchen sink is leaking", "Water dripping under the kitchen sink, need urgent repair.", "Chilanzar 9, Block 3, Apt 42", "completed"),
    (0, "malika_clean", 0, "Spring deep cleaning", "Need full apartment cleaned before guests arrive this weekend.", "Mirzo Ulugbek, 15-A, Apt 8", "completed"),
    (1, "aziz_electric", 0, "Wiring check in old house", "Bought an old house, need full wiring inspection before renovation.", "Sergeli, Yangi Hayot, House 22", "accepted"),
    (1, "bobur_wood", 0, "New bookshelves for study", "Need 3 custom bookshelves for my home office, oak or walnut.", "Yunusabad 4, Block 7, Apt 15", "pending"),
    (2, "rustam_painter", 0, "Repaint living room", "Walls are faded, want a fresh modern color. Room is ~25 sqm.", "Mirabad, Bunyodkor 12, Apt 3", "completed"),
    (2, "farid_master", 1, "New bathroom pipes", "Replacing old rusty pipes in the guest bathroom.", "Mirabad, Bunyodkor 12, Apt 3", "pending"),
    (0, "bobur_wood", 2, "Kitchen cabinet makeover", "Want to reface my kitchen cabinet doors, current ones are chipped.", "Chilanzar 9, Block 3, Apt 42", "accepted"),
]

created_orders = []
for ci, wname, si, title, desc, addr, order_status in orders_data:
    client = client_users[ci]
    wp = worker_profiles[wname]
    worker_services = Service.objects.filter(worker=wp).order_by("id")
    service = worker_services[si] if si < worker_services.count() else worker_services.first()

    order, created = Order.objects.get_or_create(
        title=title,
        client=client,
        defaults={
            "description": desc,
            "address": addr,
            "status": order_status,
            "worker": wp,
            "service": service,
        }
    )
    created_orders.append(order)
    print(f"  Order: '{title}' [{order_status}] by {client.first_name} -> {wp.user.first_name}")


# --- Reviews (for completed orders) ---
print("\n--- Creating Reviews ---")
reviews_data = [
    (0, 5, "Farid arrived on time and fixed the leak in 30 minutes. Excellent work, very professional!"),
    (1, 5, "Malika and her team did an amazing job. My apartment has never been this clean. Highly recommend!"),
    (4, 4, "Rustam did a good job with the painting. Color is perfect. Minor cleanup needed after, but overall satisfied."),
]

for oi, rating, comment in reviews_data:
    order = created_orders[oi]
    review, created = Review.objects.get_or_create(
        order=order,
        defaults={
            "client": order.client,
            "rating": Decimal(str(rating)),
            "comment": comment,
        }
    )
    if created:
        print(f"  Review: {rating}★ for '{order.title}' — {comment[:50]}...")


# --- Conversations & Messages ---
print("\n--- Creating Conversations & Messages ---")
convos_data = [
    # (client_idx, worker_username, messages)
    (0, "farid_master", [
        ("client", "Salom Farid aka! Oshxonadagi kran oqyapti, qachon kelishingiz mumkin?"),
        ("worker", "Vaaleykum assalom! Bugun kechqurungi 5 da bo'lsam bo'ladimi?"),
        ("client", "Juda yaxshi, kutaman! Manzilni yubordim."),
        ("worker", "Qabul qildim, ko'rishamiz 👍"),
    ]),
    (0, "malika_clean", [
        ("client", "Assalomu alaykum Malika! 3 xonali kvartira tozalash kerak, narxi qancha bo'ladi?"),
        ("worker", "Vaaleykum assalom! 250,000 so'mdan boshlanadi. Qachonga kerak?"),
        ("client", "Shanba kuniga, mehmonlar keladi."),
        ("worker", "Yaxshi, shanba ertalab 8 da boshlaymiz. To'liq tozalash 4-5 soat davom etadi."),
        ("client", "Zo'r, rahmat! Kutaman."),
    ]),
    (1, "aziz_electric", [
        ("client", "Salom Aziz aka, eski uyda simlarni tekshirish kerak. Kela olasizmi?"),
        ("worker", "Salom! Ha, albatta. Qayerda joylashgan uy?"),
        ("client", "Sergeli, Yangi Hayot mahallasi. Uy ancha eski, 70-yillarda qurilgan."),
        ("worker", "Tushundim, har holda to'liq tekshiruv o'tkazamiz. Ertaga 10 da bo'lsam bo'ladimi?"),
        ("client", "Ha, juda yaxshi bo'ladi!"),
        ("worker", "Kelishildi ✅"),
    ]),
    (1, "bobur_wood", [
        ("client", "Assalomu alaykum Bobur! Ish xonasi uchun kitob javoni yasash mumkinmi?"),
        ("worker", "Vaaleykum assalom! Albatta, qanday o'lcham va material xohlaysiz?"),
        ("client", "3 ta javon, yong'oq yog'ochidan, har biri 2 metr balandlikda."),
        ("worker", "Yaxshi, ishni boshlashdan oldin o'lchab ko'rish kerak. Bir kuni kelib ko'ray."),
    ]),
    (2, "rustam_painter", [
        ("client", "Salom Rustam! Mehmonxona devorlarini bo'yatish kerak, qanday rang tavsiya qilasiz?"),
        ("worker", "Salom! Hozir zamonaviy kulrang va oq aralash ranglar trend. Xona necha kv metr?"),
        ("client", "Taxminan 25 kv metr. Kulrang variant yoqadi!"),
        ("worker", "Zo'r tanlov! Premium bo'yoq bilan 280,000 so'm atrofida bo'ladi. Kelishaylikmi?"),
        ("client", "Ha, boshlaymiz! Qachon boshlay olasiz?"),
        ("worker", "Bu haftaning oxirida boshlay olamiz 🎨"),
    ]),
]

for ci, wname, msgs in convos_data:
    client = client_users[ci]
    worker_user = worker_profiles[wname].user

    conv, _ = Conversation.objects.get_or_create(
        client=client,
        worker=worker_user,
    )
    print(f"  Conversation: {client.first_name} <-> {worker_user.first_name}")

    for role, text in msgs:
        sender = client if role == "client" else worker_user
        msg, created = Message.objects.get_or_create(
            conversation=conv,
            sender=sender,
            message=text,
            defaults={"message_type": "text"}
        )
        if created:
            print(f"    [{sender.first_name}]: {text[:60]}...")


# --- Portfolios ---
print("\n--- Creating Portfolios ---")

portfolios_data = [
    {
        "worker_username": "farid_master",
        "title": "Modern Bathroom Remodel",
        "description": "Complete overhaul of master bathroom piping and faucet fixtures. Installed copper plumbing and high-end wall-mounted toilets.",
        "category_name": "Plumbing",
        "local_img": "demo_images/bathroom_plumbing.png"
    },
    {
        "worker_username": "aziz_electric",
        "title": "Smart Home Control Panel Setup",
        "description": "Installation of a modern smart lighting circuit breaker panel. Custom programmed dimmers, sensors, and remote app integration.",
        "category_name": "Electrical",
        "local_img": "demo_images/smart_home_panel.png"
    },
    {
        "worker_username": "malika_clean",
        "title": "Post-Renovation House Clean",
        "description": "Intense deep cleaning of a 4-bedroom villa after construction. All paint residues, dust, and construction debris completely removed.",
        "category_name": "Cleaning",
        "local_img": "demo_images/house_clean.png"
    },
    {
        "worker_username": "rustam_painter",
        "title": "Feature Accent Wall Painting",
        "description": "High-end geometric feature wall painting in a modern minimalist apartment. Used premium matte textured eco-paints.",
        "category_name": "Painting",
        "local_img": "demo_images/accent_wall.png"
    },
    {
        "worker_username": "bobur_wood",
        "title": "Handcrafted Walnut Bookshelves",
        "description": "Custom floor-to-ceiling bookshelves made from solid dark walnut wood, complete with integrated LED backlight panels.",
        "category_name": "Carpentry",
        "local_img": "demo_images/walnut_bookshelves.png"
    }
]

for p_data in portfolios_data:
    wp = worker_profiles.get(p_data["worker_username"])
    if not wp:
        continue

    p, created = Portfolio.objects.get_or_create(
        worker=wp,
        title=p_data["title"],
        defaults={
            "description": p_data["description"],
            "category": cats[p_data["category_name"]]
        }
    )
    if created or not p.image:
        try:
            print(f"  Setting image for '{p_data['title']}'...")
            from django.conf import settings
            local_path = os.path.join(settings.BASE_DIR, p_data["local_img"])
            if os.path.exists(local_path):
                with open(local_path, "rb") as f:
                    p.image.save(f"portfolio_{p_data['worker_username']}.png", File(f), save=True)
                print(f"    Saved portfolio: {p.title}")
            else:
                print(f"    Local image not found: {local_path}")
        except Exception as e:
            print(f"    Failed to set image: {e}")
            pass

print("\n=== Seed Complete! ===")
print(f"  Workers: {len(workers_data)}")
print(f"  Clients: {len(clients_data)}")
print(f"  Services: {len(all_services)}")
print(f"  Orders: {len(orders_data)}")
print(f"  Reviews: {len(reviews_data)}")
print(f"  Conversations: {len(convos_data)}")
print(f"  Portfolios: {len(portfolios_data)}")
print("\n  All demo accounts use password: Demo1234!")
