from django import template

register = template.Library()


@register.filter
def split_csv(value: str):
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


@register.filter
def dict_get(mapping, key):
    if not mapping:
        return ""
    return mapping.get(key, "")
