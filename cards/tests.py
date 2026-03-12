from __future__ import annotations

import io
import tempfile
from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .image_search import compute_color_histogram_signature
from .models import CardImage, KnowledgeCard


def _make_test_image(name: str, color=(200, 100, 80)):
    image_io = io.BytesIO()
    image = Image.new("RGB", (64, 64), color)
    image.save(image_io, format="PNG")
    image_io.seek(0)
    return SimpleUploadedFile(name=name, content=image_io.read(), content_type="image/png")


TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CardFlowTests(TestCase):
    def test_create_card_with_image(self):
        image_file = _make_test_image("cat.png")
        response = self.client.post(
            reverse("cards:create"),
            {
                "title": "Persian Cat",
                "category": "Animal",
                "summary": "calm cat",
                "description": "long hair",
                "tags": "cat,pet",
                "keywords": "fluffy",
                "images": image_file,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(KnowledgeCard.objects.count(), 1)
        self.assertEqual(CardImage.objects.count(), 1)

    def test_keyword_search(self):
        card = KnowledgeCard.objects.create(
            title="Lavender",
            category="Plant",
            summary="aromatic flower",
            description="used for calming",
            tags="flower,herb",
            keywords="purple",
        )
        image = _make_test_image("lav.png")
        signature = compute_color_histogram_signature(image)
        CardImage.objects.create(card=card, image=image, original_filename="lav.png", average_hash=signature)

        response = self.client.get(reverse("cards:browse"), {"q": "aromatic"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lavender")

    def test_image_search(self):
        card = KnowledgeCard.objects.create(
            title="Camera",
            category="Object",
            summary="photo device",
            description="",
            tags="lens",
            keywords="",
        )
        stored_image = _make_test_image("camera.png", color=(120, 120, 120))
        signature = compute_color_histogram_signature(stored_image)
        CardImage.objects.create(card=card, image=stored_image, original_filename="camera.png", average_hash=signature)

        response = self.client.post(
            reverse("cards:search_image"),
            {"query_image": _make_test_image("query.png", color=(120, 120, 120))},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Camera")


def tearDownModule():
    for path in Path(TEMP_MEDIA_ROOT).glob("**/*"):
        if path.is_file():
            path.unlink()
    for path in sorted(Path(TEMP_MEDIA_ROOT).glob("**/*"), reverse=True):
        if path.is_dir():
            path.rmdir()
