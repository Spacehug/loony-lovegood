from django.urls import path, register_converter

from core.converters import NegativeIntConverter
from core.views import (
    ProfileListCreateView,
    ProfileRetrieveUpdateDestroyView,
    ProfileResetGraceView,
    ProfileWarningIncreaseView,
    ProfileWarningDecreaseView,
)

register_converter(NegativeIntConverter, "negint")

urlpatterns = [
    path("", ProfileListCreateView.as_view()),
    path("<int:uid>/<negint:gid>/", ProfileRetrieveUpdateDestroyView.as_view()),
    path("<int:uid>/<negint:gid>/grace/reset/", ProfileResetGraceView.as_view()),
    path("<int:uid>/<negint:gid>/warning/", ProfileWarningIncreaseView.as_view()),
    path("<int:uid>/<negint:gid>/pardon/", ProfileWarningDecreaseView.as_view()),
]
