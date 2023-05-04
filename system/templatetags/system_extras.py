from django import template

register = template.Library()

@register.filter
def sort_lower(lst):
    ordering = [
        "Book",
        "ThesisBook",
    ]

    #sorted = lst.sort(key=lambda x: ordering.index(x['object_name']) if x['object_name'] in ordering else 3)
    sort = sorted(lst, key=lambda x: ordering.index(x['object_name']) if x['object_name'] in ordering else 3)
    return sort
    # return sorted(lst, key=lambda item: getattr(item, key_name).lower())