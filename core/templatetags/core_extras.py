from django import template
from django.utils.safestring import mark_safe

from syncprojectsweb.settings import SENTRY_JS_SCRIPT

register = template.Library()


@register.simple_tag
@mark_safe
def sentry_js_script():
    return SENTRY_JS_SCRIPT
