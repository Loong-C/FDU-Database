from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from accounts.jwt import issue_token_pair, revoke_refresh_token, rotate_refresh_token

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "password",
            "email",
            "first_name",
            "last_name",
            "display_name",
            "role",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        if not password:
            raise serializers.ValidationError({"password": "创建用户时必须提供密码。"})
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(trim_whitespace=False)

    def validate(self, attrs):
        user = authenticate(username=attrs["username"], password=attrs["password"])
        if not user or not user.is_active:
            raise serializers.ValidationError("用户名或密码错误。")
        attrs["user"] = user
        return attrs

    def create(self, validated_data):
        return issue_token_pair(validated_data["user"])


class RefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def create(self, validated_data):
        return rotate_refresh_token(validated_data["refresh_token"])


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def create(self, validated_data):
        revoke_refresh_token(validated_data["refresh_token"])
        return {}
