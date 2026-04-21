from datetime import date

from rest_framework import serializers

from common.validators import validate_phone
from customers.models import Customer, Member


class CustomerSerializer(serializers.ModelSerializer):
    is_member = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            "customer_id",
            "customer_name",
            "phone",
            "email",
            "address",
            "register_time",
            "status",
            "is_member",
        ]
        read_only_fields = ["customer_id", "register_time", "is_member"]

    def validate_phone(self, value):
        return validate_phone(value)

    def get_is_member(self, instance):
        return hasattr(instance, "member")


class MemberReadSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(source="customer.customer_id", read_only=True)
    customer_name = serializers.CharField(source="customer.customer_name", read_only=True)
    phone = serializers.CharField(source="customer.phone", read_only=True)
    email = serializers.EmailField(source="customer.email", read_only=True)
    address = serializers.CharField(source="customer.address", read_only=True)
    customer_status = serializers.CharField(source="customer.status", read_only=True)

    class Meta:
        model = Member
        fields = [
            "customer_id",
            "customer_name",
            "phone",
            "email",
            "address",
            "customer_status",
            "member_no",
            "level",
            "points",
            "join_date",
        ]


class MemberWriteSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField(required=False)
    member_no = serializers.CharField(max_length=50, required=False)
    level = serializers.ChoiceField(choices=Member.LEVEL_CHOICES, required=False)
    points = serializers.IntegerField(min_value=0, required=False)
    join_date = serializers.DateField(required=False)

    def validate_join_date(self, value):
        if value > date.today():
            raise serializers.ValidationError("入会日期不能晚于今天。")
        return value
