from rest_framework import serializers

from common.validators import validate_phone
from stores.models import Store


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = [
            "store_id",
            "store_name",
            "city",
            "address",
            "phone",
            "manager_name",
            "created_at",
        ]
        read_only_fields = ["store_id", "created_at"]

    def validate_phone(self, value):
        return validate_phone(value)
