from django.contrib import admin

from .models import CardImage, KnowledgeCard


class CardImageInline(admin.TabularInline):
    model = CardImage
    extra = 0


@admin.register(KnowledgeCard)
class KnowledgeCardAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "created_at")
    search_fields = ("title", "summary", "description", "tags", "keywords")
    list_filter = ("category", "created_at")
    inlines = [CardImageInline]
