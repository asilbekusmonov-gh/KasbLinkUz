"""
WSGI config for kasblinkuz project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import shutil
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "root.settings")

# When using persistent volumes, the media directory might be empty.
# This copies demo images to the media volume on startup so they are available.
try:
    from root.settings import BASE_DIR, MEDIA_ROOT
    demo_media_dir = os.path.join(BASE_DIR, "demo_media")
    target_dir = os.path.join(MEDIA_ROOT, "portfolio", "demo")
    
    if os.path.exists(demo_media_dir):
        os.makedirs(target_dir, exist_ok=True)
        for filename in os.listdir(demo_media_dir):
            src = os.path.join(demo_media_dir, filename)
            dst = os.path.join(target_dir, filename)
            if os.path.isfile(src) and not os.path.exists(dst):
                shutil.copy2(src, dst)
except Exception as e:
    print("Warning: Failed to copy demo media files:", e)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

try:
    from apps.models import Portfolio
    for p in Portfolio.objects.all():
        if not p.image or not os.path.exists(os.path.join(settings.MEDIA_ROOT, str(p.image))):
            # Find a matching demo image based on category
            cat_name = p.category.name.lower() if p.category else ""
            demo_img = "bathroom_plumbing.png"
            if "electric" in cat_name: demo_img = "smart_home_panel.png"
            elif "clean" in cat_name: demo_img = "house_clean.png"
            elif "paint" in cat_name: demo_img = "accent_wall.png"
            elif "carpent" in cat_name: demo_img = "walnut_bookshelves.png"
            
            p.image = f"portfolio/demo/{demo_img}"
            p.save()
            print(f"Fixed dangling image for portfolio: {p.title}")
except Exception as e:
    print("Warning: Failed to fix dangling portfolio images:", e)
