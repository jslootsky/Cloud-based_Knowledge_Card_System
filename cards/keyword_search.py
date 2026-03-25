from __future__ import annotations
from django.db.models import Q


def apply_keyword_search(queryset, keyword: str):
    if not keyword:
        return queryset
    
    #split query into words
    terms = keyword.strip().split()

    query = Q()

    for term in terms:
        query &= (
            Q(title__icontains=term) | Q(summary__icontains=term) | Q(description__icontains=term) | Q(tags__icontains=term) | Q(keywords__icontains=term)
        )

    return queryset.filter(query)
