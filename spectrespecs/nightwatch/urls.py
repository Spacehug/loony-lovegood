from django.urls import path

from nightwatch.views import MessageCheckView

urlpatterns = [
    path("", MessageCheckView.as_view()),
]
