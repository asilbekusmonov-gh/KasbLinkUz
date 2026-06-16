"""
Load Uzbekistan regions and districts from CSV files.
Run: uv run python load_locations.py
"""
import csv
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "root.settings")

import django

django.setup()

from apps.models.users import City, District
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"


def load_locations():
    regions_path = DATA_DIR / "regions.csv"
    districts_path = DATA_DIR / "districts.csv"

    if not regions_path.exists() or not districts_path.exists():
        raise FileNotFoundError(f"Missing CSV files in {DATA_DIR}")

    print("Loading regions (cities)...")
    with regions_path.open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            city, created = City.objects.update_or_create(
                id=int(row["id"]),
                defaults={"name": row["name"].strip()},
            )
            action = "created" if created else "updated"
            print(f"  [{action}] {city.name}")

    print("Loading districts...")
    with districts_path.open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            city = City.objects.get(id=int(row["region"]))
            district, created = District.objects.update_or_create(
                id=int(row["id"]),
                defaults={
                    "name": row["name"].strip(),
                    "city": city,
                },
            )
            action = "created" if created else "updated"
            print(f"  [{action}] {district.name} ({city.name})")

    print(f"\nDone: {City.objects.count()} regions, {District.objects.count()} districts.")


if __name__ == "__main__":
    load_locations()
