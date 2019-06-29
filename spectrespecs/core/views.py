from rest_framework.generics import ListCreateAPIView, GenericAPIView
from rest_framework.mixins import (
    UpdateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
)

from core.mixins import MultipleFieldLookupMixin
from core.models import Profile
from core.serializers import (
    ProfileSerializer,
    ProfileGraceSerializer,
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


# Todo: delete this
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


class ProfileModifyWarningView(MultipleFieldLookupMixin, UpdateAPIView):
    serializer_class = ProfileWarningSerializer
    queryset = Profile.objects.all()
    lookup_fields = ("uid", "gid")

    def perform_update(self, serializer):
        modifier = self.request.data.get("warning", 0)
        serializer.instance.modify_warning_count(modifier)
        serializer.save()
