from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def days_since(hired_at):
    """Вернуть стаж работы в днях от даты приёма до сегодня."""
    if not hired_at:
        return None
    today = timezone.now().date()
    if hasattr(hired_at, "date"):
        hired_at = hired_at.date()
    delta = today - hired_at
    return delta.days if delta.days >= 0 else 0
