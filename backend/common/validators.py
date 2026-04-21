import re
from datetime import date

from rest_framework import serializers


PHONE_RE = re.compile(r"^\+?[0-9\-() ]{7,20}$")


def validate_phone(value: str | None) -> str | None:
    if not value:
        return value
    if not PHONE_RE.match(value):
        raise serializers.ValidationError("电话号码格式不正确。")
    return value


def validate_publish_date(value):
    if value and value > date.today():
        raise serializers.ValidationError("出版日期不能晚于当前日期。")
    return value
