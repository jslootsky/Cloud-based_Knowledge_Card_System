from __future__ import annotations

import io

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image

from cards.image_search import compute_color_histogram_signature
from cards.models import CardImage, KnowledgeCard


SEED_DATA = [
    ("Persian Cat", "Animal", "Long-haired calm domestic cat.", "persian,cat,pet,fluffy", "indoor,cat breed", (220, 210, 210)),
    ("Golden Retriever", "Animal", "Friendly and active dog breed.", "dog,pet,family,active", "retriever,dog breed", (230, 210, 160)),
    ("Lavender", "Plant", "Aromatic flowering plant.", "flower,herb,aroma", "purple,calming", (180, 160, 220)),
    ("Vintage Camera", "Object", "Classic film camera object.", "object,lens,film", "photography,analog", (160, 170, 180)),
]


class Command(BaseCommand):
    help = "Seed sample knowledge cards for local demo"

    def handle(self, *args, **options):
        for title, category, summary, tags, keywords, color in SEED_DATA:
            card, created = KnowledgeCard.objects.get_or_create(
                title=title,
                defaults={
                    "category": category,
                    "summary": summary,
                    "description": summary,
                    "tags": tags,
                    "keywords": keywords,
                },
            )
            if not created:
                continue

            image_io = io.BytesIO()
            image = Image.new("RGB", (720, 480), color)
            image.save(image_io, format="PNG")
            image_io.seek(0)
            image_name = f"{title.lower().replace(' ', '_')}.png"

            hash_value = compute_color_histogram_signature(image_io)
            image_io.seek(0)

            django_file = ContentFile(image_io.read(), name=image_name)
            CardImage.objects.create(
                card=card,
                image=django_file,
                original_filename=image_name,
                average_hash=hash_value,
            )

        self.stdout.write(self.style.SUCCESS("Seed data is ready."))
