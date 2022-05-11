from django.urls import path 

from .views.registry import RegistryView, PendingView, MineView

urlpatterns = [
    path("registry/", RegistryView.as_view()),
    path("registry/<int:id_>", RegistryView.as_view()),

    path("pending/", PendingView.as_view()),
    path("mine/", MineView.as_view()),
]