from django.urls import path 

from .views.registry import RegistryView, PendingView, MineView, NewNodeView, RegisterNodeView, BlockSyncView

urlpatterns = [
    path("registry/", RegistryView.as_view()),
    path("registry/<int:id_>", RegistryView.as_view()),

    path("pending/", PendingView.as_view()),
    path("mine/", MineView.as_view()),

    path("register_node/", NewNodeView.as_view()),
    path("register_with/", RegisterNodeView.as_view()),
    path("sync_block/", BlockSyncView.as_view()),

]