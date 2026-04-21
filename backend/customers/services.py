from rest_framework import serializers

from customers.models import Customer, Member


def create_member(validated_data):
    customer_id = validated_data.get("customer_id")
    if customer_id is None:
        raise serializers.ValidationError({"customer_id": "customer_id 为必填字段。"})

    customer = Customer.objects.filter(pk=customer_id).first()
    if not customer:
        raise serializers.ValidationError({"customer_id": "客户不存在。"})
    if hasattr(customer, "member"):
        raise serializers.ValidationError({"customer_id": "该客户已经是会员。"})

    return Member.objects.create(customer=customer, **{k: v for k, v in validated_data.items() if k != "customer_id"})


def update_member(instance, validated_data):
    customer_id = validated_data.pop("customer_id", None)
    if customer_id is not None and customer_id != instance.customer_id:
        raise serializers.ValidationError({"customer_id": "会员绑定客户不可修改。"})

    for attr, value in validated_data.items():
        setattr(instance, attr, value)
    instance.save()
    return instance
