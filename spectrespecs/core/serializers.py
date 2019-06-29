from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from core.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            "uid",
            "gid",
            "has_messages",
            "created_at",
            "grace_at",
            "warnings",
        )
        extra_kwargs = {
            "created_at": {"read_only": True},
            "grace_at": {"read_only": True},
        }
        validators = [
            UniqueTogetherValidator(
                queryset=Profile.objects.all(), fields=("uid", "gid")
            )
        ]


class ProfileGraceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("uid", "gid", "grace_at")
        extra_kwargs = {
            "uid": {"read_only": True},
            "gid": {"read_only": True},
            "grace_at": {"read_only": True},
        }


class ProfileWarningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("uid", "gid", "warnings")
        extra_kwargs = {
            "uid": {"read_only": True},
            "gid": {"read_only": True},
            "warnings": {"read_only": True},
        }
