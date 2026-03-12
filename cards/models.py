from __future__ import annotations

from django.db import models


class KnowledgeCard(models.Model):
    CATEGORY_CHOICES = [
        ("Animal", "Animal"),
        ("Plant", "Plant"),
        ("Object", "Object"),
        ("Other", "Other"),
    ]

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="Other")
    summary = models.TextField()
    description = models.TextField(blank=True)
    tags = models.CharField(max_length=300, help_text="Comma separated tags")
    keywords = models.CharField(max_length=500, blank=True, help_text="Optional extra keywords")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    @property
    def tag_list(self) -> list[str]:
        return [tag.strip() for tag in self.tags.split(",") if tag.strip()]

    @property
    def keyword_list(self) -> list[str]:
        merged = set(self.tag_list)
        for item in self.keywords.split(","):
            token = item.strip()
            if token:
                merged.add(token)
        return sorted(merged)


class CardImage(models.Model):
    card = models.ForeignKey(KnowledgeCard, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="knowledge_cards/%Y/%m/%d")
    original_filename = models.CharField(max_length=255)
    average_hash = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"{self.card.title} - {self.original_filename}"

    @property
    def storage_key(self) -> str:
        return self.image.name

    @property
    def image_url(self) -> str:
        if not self.image:
            return ""
        return self.image.url
