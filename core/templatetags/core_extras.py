from django import template

register = template.Library()


@register.simple_tag
def liked_by_user(comment, user):
    if comment.liked_by(user):
        return "btn-primary "
    return ""
