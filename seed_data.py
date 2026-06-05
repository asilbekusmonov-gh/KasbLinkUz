import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'root.settings')
django.setup()

from apps.models import User, WorkerProfile, Category, Service
from django.contrib.auth.hashers import make_password

print("Seeding database with realistic mock data...")

# Clear existing data if necessary (optional, but good for clean state)
# Service.objects.all().delete()
# WorkerProfile.objects.all().delete()
# Category.objects.all().delete()

# 1. Categories
categories_data = [
    {"name": "Santexnika", "slug": "santexnika"},
    {"name": "Elektrik xizmati", "slug": "elektrik"},
    {"name": "Uy ta'miri", "slug": "remont"},
    {"name": "Duradgorlik", "slug": "duradgor"},
    {"name": "Yuk tashish", "slug": "kuryer"},
]

cats = []
for cat_info in categories_data:
    cat, created = Category.objects.get_or_create(slug=cat_info["slug"], defaults={"name": cat_info["name"]})
    cats.append(cat)

print(f"✓ Categories seeded: {len(cats)}")

# 2. Users & Worker Profiles
workers_data = [
    {
        "username": "rustam_usta",
        "first_name": "Rustam",
        "last_name": "Karimov",
        "phone_number": "901112233",
        "bio": "12 yillik tajribaga ega professional santexnik. Kranlarni almashtirish, trubalar montaji va isitish tizimlarini ta'mirlash. Tez va sifatli xizmat!",
        "service_name": "Kran, truba va smesitel ta'mirlash",
        "min_price": 50000,
        "max_price": 250000,
        "cat_slug": "santexnika",
        "rating": 4.9,
        "orders": 24
    },
    {
        "username": "anvar_elektrik",
        "first_name": "Anvar",
        "last_name": "Solihov",
        "phone_number": "904445566",
        "bio": "Murakkablikdagi har qanday elektr ishlarini bajaramiz. Rozetkalar, lyustralar montaji, qisqa tutashuvlarni bartaraf etish. Xavfsiz va kafolatli.",
        "service_name": "Elektromontaj va lyustra o'rnatish",
        "min_price": 70000,
        "max_price": 400000,
        "cat_slug": "elektrik",
        "rating": 4.8,
        "orders": 18
    },
    {
        "username": "farhod_molyar",
        "first_name": "Farhod",
        "last_name": "Aliev",
        "phone_number": "907778899",
        "bio": "Devorlarni bo'yash, oboy yopishtirish, gipsokarton ishlari va kosmetik ta'mirlash. Xonadoningizga yangi nafas beramiz.",
        "service_name": "Devor bo'yash va oboy yopishtirish",
        "min_price": 100000,
        "max_price": 800000,
        "cat_slug": "remont",
        "rating": 4.7,
        "orders": 31
    },
    {
        "username": "sherzod_mebel",
        "first_name": "Sherzod",
        "last_name": "Mansurov",
        "phone_number": "935554433",
        "bio": "Mebel yig'ish va ta'mirlash xizmatlari. Oshxona mebeli, shkaf va krovatlarni tez fursatda yig'ib beramiz. Asbob-uskunalar o'zimizniki.",
        "service_name": "Mebel yig'ish va ta'mirlash",
        "min_price": 80000,
        "max_price": 500000,
        "cat_slug": "duradgor",
        "rating": 4.9,
        "orders": 15
    }
]

for w in workers_data:
    user, created = User.objects.get_or_create(
        username=w["username"],
        defaults={
            "email": f"{w['username']}@kasblink.uz",
            "password": make_password("password123"),
            "first_name": w["first_name"],
            "last_name": w["last_name"],
            "phone_number": w["phone_number"],
            "role": User.Role.WORKER
        }
    )
    
    # Get or create worker profile
    profile, p_created = WorkerProfile.objects.get_or_create(
        user=user,
        defaults={
            "bio": w["bio"],
            "work_start_time": timezone.now(),
            "work_end_time": timezone.now(),
            "rating": w["rating"],
            "completed_orders_count": w["orders"],
            "is_available": True
        }
    )
    
    # Create service
    cat = Category.objects.get(slug=w["cat_slug"])
    Service.objects.get_or_create(
        worker=profile,
        category=cat,
        defaults={
            "name": w["service_name"],
            "min_price": w["min_price"],
            "max_price": w["max_price"],
            "active": True,
            "description": w["bio"]
        }
    )

print("✓ Workers and Services seeded successfully.")

# 3. Create a Customer account
User.objects.get_or_create(
    username="mijoz1",
    defaults={
        "email": "mijoz1@kasblink.uz",
        "password": make_password("password123"),
        "first_name": "Asrorbek",
        "last_name": "Usmonov",
        "phone_number": "900000001",
        "role": User.Role.CUSTOMER
    }
)
print("✓ Customer account seeded: username='mijoz1', password='password123'")
print("Database Seeding Completed!")
