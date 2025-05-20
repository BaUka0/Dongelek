from django import template

register = template.Library()

@register.filter
def map_attr(queryset, attr_name):
    return [getattr(item, attr_name) for item in queryset]