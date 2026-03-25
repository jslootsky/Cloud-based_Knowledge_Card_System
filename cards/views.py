from __future__ import annotations

from dataclasses import dataclass

from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    CardImageUploadForm,
    ImageSearchForm,
    KeywordSearchForm,
    KnowledgeCardForm,
    KnowledgeCardUpdateForm,
)
from .image_search import compute_color_histogram_signature
from .image_similarity import compare_image_similarity
from .keyword_search import apply_keyword_search
from .models import CardImage, KnowledgeCard

IMAGE_TOP_K = 3


@dataclass
class ImageMatch:
    card_id: int
    similarity: float


def _apply_sort(queryset, sort: str):
    if sort == "title":
        return queryset.order_by("title")
    if sort == "oldest":
        return queryset.order_by("created_at")
    return queryset.order_by("-created_at")


def _save_images(card: KnowledgeCard, files) -> None:
    # TODO(student): implement image save/replace logic for one-primary-image policy.
    # HINT: take files[0], compute histogram signature, then upsert CardImage for this card.
    # Default fallback keeps app runnable but does not compute signatures.
    if not files:
        return
    uploaded = files[0]
    existing = card.images.first()

    histogram_signature = compute_color_histogram_signature(uploaded) #computing histogram signature for the uploaded image

    if existing:
        existing.image.delete(save=False)
        existing.image = uploaded
        existing.original_filename = uploaded.name
        existing.average_hash = ""
        existing.histogram_signature = histogram_signature
        existing.save(update_fields=["image", "original_filename", "average_hash", "histogram_signature"])
    else:
        CardImage.objects.create(
            card=card,
            image=uploaded,
            original_filename=uploaded.name,
            average_hash="",
            histogram_signature=histogram_signature,
        )


def home(request: HttpRequest) -> HttpResponse:
    card_count = KnowledgeCard.objects.count()
    image_count = CardImage.objects.count()

    context = {
        "active_nav": "dashboard",
        "card_count": card_count,
        "image_count": image_count,
        "recent_cards": KnowledgeCard.objects.prefetch_related("images").all()[:6],
    }
    return render(request, "cards/dashboard.html", context)


def create_card(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = KnowledgeCardForm(request.POST, request.FILES)
        files = request.FILES.getlist("images")

        if form.is_valid() and files:
            card = form.save()
            _save_images(card, files)
            messages.success(request, "Knowledge card created with one primary image.")
            return redirect("cards:detail", card_id=card.id)

        if not files:
            form.add_error("images", "Please upload at least one image.")
    else:
        form = KnowledgeCardForm()

    return render(request, "cards/create_card.html", {"form": form, "active_nav": "create"})


def browse_cards(request: HttpRequest) -> HttpResponse:
    initial = {"sort": request.GET.get("sort", "recent")}
    form = KeywordSearchForm(request.GET or None, initial=initial)
    image_form = ImageSearchForm()

    cards = KnowledgeCard.objects.prefetch_related("images").all()
    query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "recent")

    if form.is_valid():
        query = form.cleaned_data.get("q", "").strip()
        sort = form.cleaned_data.get("sort") or "recent"

    if query:
        cards = apply_keyword_search(cards, query)

    cards = _apply_sort(cards, sort)

    paginator = Paginator(cards, 9)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "form": form,
        "image_form": image_form,
        "page_obj": page_obj,
        "result_count": paginator.count,
        "query": query,
        "sort": sort,
        "active_nav": "browse",
        "image_search_mode": False,
        "match_scores": {},
        "match_ranks": {},
        "image_search_meta": {},
    }
    return render(request, "cards/browse_cards.html", context)


def image_search(request: HttpRequest) -> HttpResponse:
    if request.method != "POST":
        return redirect("cards:browse")

    form = KeywordSearchForm(initial={"sort": "recent"})
    image_form = ImageSearchForm(request.POST, request.FILES)

    if not image_form.is_valid():
        messages.error(request, "Please provide a valid image for search.")
        return redirect("cards:browse")

    query_image = image_form.cleaned_data["query_image"]
    query_signature = compute_color_histogram_signature(query_image)

    # TODO(student): implement image similarity ranking.
    # HINT:
    # 1) iterate CardImage rows with non-empty signatures
    # 2) call compare_image_similarity(query_signature, stored_signature)
    # 3) keep best score per card, sort desc, return top IMAGE_TOP_K
    # Default fallback: first 3 cards with images, all scores 0.

    #store best similarity score per card
    best_scores_by_card: dict[int, float] = {}

    stored_images = CardImage.objects.select_related("card").exclude(
        histogram_signature=""
    )

    for stored_image in stored_images:
        try:
            similarity = compare_image_similarity(
                query_signature,
                stored_image.histogram_signature,
            )
        except ValueError:
            #skip invalid
            continue

        card_id = stored_image.card_id
        current_best = best_scores_by_card.get(card_id)

        if current_best is None or similarity > current_best:
            best_scores_by_card[card_id] = similarity

    ranked_matches = sorted(best_scores_by_card.items(), key=lambda item: item[1], reverse=True)[:IMAGE_TOP_K]

    ordered_card_ids = [card_id for card_id, _score in ranked_matches]
    match_scores = {card_id: score for card_id, score in ranked_matches}
    match_ranks ={
        card_id: idx + 1 for idx, (card_id, _score) in enumerate(ranked_matches)
    }

    #fetch in ranked order
    cards_by_id = {
        card.id: card
        for card in KnowledgeCard.object.prefetch_related("images").filter(
            id_in=ordered_card_ids
        )
    }

    ordered_cards = [cards_by_id[card_id] for card_id in ordered_card_ids if card_id in cards_by_id]

    paginator = Paginator(ordered_cards, 9)
    page_obj = paginator.get_page(request.GET.get("page"))

    paginator = Paginator(ordered_cards, 9)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "form": form,
        "image_form": image_form,
        "page_obj": page_obj,
        "result_count": paginator.count,
        "query": "",
        "sort": "relevance",
        "active_nav": "browse",
        "image_search_mode": True,
        "match_scores": match_scores,
        "match_ranks": match_ranks,
        "image_search_meta": {
            "query_name": getattr(query_image, "name", "uploaded image"),
            "top_k": IMAGE_TOP_K,
        },
    }
    return render(request, "cards/browse_cards.html", context)


def card_detail(request: HttpRequest, card_id: int) -> HttpResponse:
    card = get_object_or_404(KnowledgeCard.objects.prefetch_related("images"), id=card_id)
    image_upload_form = CardImageUploadForm()
    context = {
        "card": card,
        "active_nav": "browse",
        "image_upload_form": image_upload_form,
    }
    return render(request, "cards/card_detail.html", context)


def edit_card(request: HttpRequest, card_id: int) -> HttpResponse:
    card = get_object_or_404(KnowledgeCard, id=card_id)
    if request.method == "POST":
        form = KnowledgeCardUpdateForm(request.POST, instance=card)
        if form.is_valid():
            form.save()
            messages.success(request, "Card updated.")
            return redirect("cards:detail", card_id=card.id)
    else:
        form = KnowledgeCardUpdateForm(instance=card)
    context = {"form": form, "card": card, "active_nav": "create", "is_edit": True}
    return render(request, "cards/create_card.html", context)


def delete_card(request: HttpRequest, card_id: int) -> HttpResponse:
    card = get_object_or_404(KnowledgeCard, id=card_id)
    if request.method == "POST":
        card.delete()
        messages.success(request, "Card deleted.")
        return redirect("cards:browse")
    return redirect("cards:detail", card_id=card_id)


def add_images(request: HttpRequest, card_id: int) -> HttpResponse:
    card = get_object_or_404(KnowledgeCard, id=card_id)
    if request.method != "POST":
        return redirect("cards:detail", card_id=card.id)

    form = CardImageUploadForm(request.POST, request.FILES)
    files = request.FILES.getlist("images")
    if form.is_valid() and files:
        _save_images(card, files)
        messages.success(request, "Primary image replaced.")
    else:
        messages.error(request, "Please select images to upload.")

    return redirect("cards:detail", card_id=card.id)
