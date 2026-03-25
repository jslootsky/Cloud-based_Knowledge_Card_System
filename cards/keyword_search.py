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
            Q(title_icontains=term) | Q(summary_icontains=term) | Q(description_icontains=term) | Q(tags_icontains=term) | Q(keyword_icontains=term)
        )
    return queryset
