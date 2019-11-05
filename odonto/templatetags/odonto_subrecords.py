"""
Odonto Subrecord rendering
"""
from django import template
from opal.templatetags import forms
from django.db import models

register = template.Library()


@register.inclusion_tag('templatetags/subrecord_row.html', takes_context=True)
def subrecord_row(context, model, object_list=None, pathway=None):
    if not object_list:
        if pathway:
            object_list = "editing.{}".format(model.get_api_name())
            if model._is_singleton:
                object_list = "[{}]".format(object_list)
        else:
            object_list = "episode.{}".format(model.get_api_name())
    return {
        'model': model,
        'object_list': object_list
    }


@register.inclusion_tag('templatetags/table_row_field_display.html')
def table_row_field_display(model_and_field):
    model, field = forms._model_and_field_from_path(model_and_field)
    ctx = {
        "model": "item.{}".format(field.attname),
        "display_name": model._get_field_title(field.attname)
    }
    if isinstance(field, (models.BooleanField, models.NullBooleanField,)):
        ctx["is_boolean"] = True
    if isinstance(field, models.DateField):
        ctx["is_date"] = True
    return ctx
