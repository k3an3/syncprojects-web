from django import template

from syncprojectsweb.settings import SENTRY_JS_SCRIPT

register = template.Library()


@register.simple_tag
def sentry_js_script():
    return SENTRY_JS_SCRIPT
