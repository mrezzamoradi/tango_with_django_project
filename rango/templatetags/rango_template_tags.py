from django import template
from rango.models import Category
from django.core import serializers

register = template.Library()


@register.inclusion_tag('rango/cats.html')
def get_categroy_list(cat=None):
    return {'cats': Category.objects.all(),
            'act_cat': cat}
