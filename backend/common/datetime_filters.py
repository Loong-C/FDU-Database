from datetime import datetime, time

from django.utils import timezone


def build_local_date_bounds(date_from=None, date_to=None):
    current_tz = timezone.get_current_timezone()
    start = None
    end = None
    if date_from:
        start = timezone.make_aware(datetime.combine(date_from, time.min), current_tz)
    if date_to:
        end = timezone.make_aware(datetime.combine(date_to, time.max), current_tz)
    return start, end


def apply_local_date_range(queryset, field_name: str, date_from=None, date_to=None):
    start, end = build_local_date_bounds(date_from, date_to)
    if start:
        queryset = queryset.filter(**{f"{field_name}__gte": start})
    if end:
        queryset = queryset.filter(**{f"{field_name}__lte": end})
    return queryset
