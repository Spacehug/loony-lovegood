from django.db.models import F
from rest_framework.generics import CreateAPIView, GenericAPIView, ListCreateAPIView
from rest_framework.mixins import (
    DestroyModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.response import Response

from core.mixins import MultipleFieldLookupMixin
from core.models import Profile
from core.serializers import (
    ProfileGraceSerializer,
    ProfileSerializer,
    ProfileWarningSerializer,
)


class RetrieveUpdateDestroyAPIView(
    RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, GenericAPIView
):
    """
    Concrete view for retrieving, updating or deleting a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class UpdateAPIView(UpdateModelMixin, GenericAPIView):
    """
    Concrete view for updating a model instance.
    """

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class ProfileListCreateView(ListCreateAPIView):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()


class ProfileRetrieveUpdateDestroyView(
    MultipleFieldLookupMixin, RetrieveUpdateDestroyAPIView
):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    lookup_fields = ("uid", "gid")


class ProfileResetGraceView(MultipleFieldLookupMixin, UpdateAPIView):
    serializer_class = ProfileGraceSerializer
    queryset = Profile.objects.all()
    lookup_fields = ("uid", "gid")

    def perform_update(self, serializer):
        serializer.instance.reset_grace()
        serializer.save()


class ProfileWarningIncreaseView(MultipleFieldLookupMixin, UpdateAPIView):
    serializer_class = ProfileWarningSerializer
    queryset = Profile.objects.all()
    lookup_fields = ("uid", "gid")

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        Profile.objects.filter(gid=instance.gid, uid=instance.uid).update(
            warnings=F("warnings") + 1
        )
        return self.update(request, *args, **kwargs)


class ProfileWarningDecreaseView(MultipleFieldLookupMixin, UpdateAPIView):
    serializer_class = ProfileWarningSerializer
    queryset = Profile.objects.all()
    lookup_fields = ("uid", "gid")

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        Profile.objects.filter(gid=instance.gid, uid=instance.uid).update(
            warnings=F("warnings") - 1
        )
        return self.update(request, *args, **kwargs)
