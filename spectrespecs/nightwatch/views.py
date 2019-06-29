from django.utils import timezone
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from core.models import Profile
from nightwatch.serializers import MessageSerializer
from nightwatch.utils import is_friend_code, is_malicious


class MessageCheckView(CreateAPIView):
    serializer_class = MessageSerializer

    def post(self, request, *args, **kwargs):
        message = request.data.get("message", None)
        uid = request.data.get("uid", None)
        gid = request.data.get("gid", None)

        if not uid and not gid:
            result = {"detail": "Can't read UID and/or GID"}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        profile, created = Profile.objects.get_or_create(uid=uid, gid=gid)

        if created:
            profile.reset_grace()

        if (
            is_malicious(message)
            and not profile.has_messages
            or not profile.has_messages
        ):
            profile.reset_grace()

        result = {
            "is_malicious": is_malicious(message),
            "is_friend_code": is_friend_code(message),
            "warnings": profile.warnings,
            "first_message": not profile.has_messages,
            "grace_at": profile.grace_at,
            "grace_diff": timezone.now() - profile.grace_at
        }
        profile.has_messages = True
        profile.save()

        return Response(result, status=status.HTTP_200_OK)
