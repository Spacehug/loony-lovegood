from rest_framework import serializers


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()
    uid = serializers.IntegerField()
    gid = serializers.IntegerField()
    grace_at = serializers.DateTimeField()

    class Meta:
        extra_kwargs = {
            "grace_at": {"read_only": True},
        }
