from django.urls import path 

from blockchain.views.registry import RegistryView
from blockchain.views.transactions import  TransactionsView
from blockchain.views.mine import MineView
from blockchain.views.nodes import NewNodeView, RegisterNodeView, BlockSyncView

urlpatterns = [
    path("registry/", RegistryView.as_view()),
    path("registry/<int:id_>", RegistryView.as_view()),

    path("pending/", TransactionsView.as_view()),
    
    path("mine/", MineView.as_view()),

    path("register_node/", NewNodeView.as_view()),
    path("register_with/", RegisterNodeView.as_view()),
    path("sync_block/", BlockSyncView.as_view()),

]