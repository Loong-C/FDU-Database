from rest_framework import serializers

from customers.models import Member


class StoreDailyQuerySerializer(serializers.Serializer):
    store_id = serializers.IntegerField(required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)


class ProductRankQuerySerializer(StoreDailyQuerySerializer):
    category_id = serializers.IntegerField(required=False)
    limit = serializers.IntegerField(required=False, min_value=1, max_value=100, default=10)


class MemberRankQuerySerializer(serializers.Serializer):
    level = serializers.ChoiceField(choices=Member.LEVEL_CHOICES, required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    limit = serializers.IntegerField(required=False, min_value=1, max_value=100, default=10)


class CategorySummaryQuerySerializer(serializers.Serializer):
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
