from django.urls import path 

from blockchain.components.registry.registry_view import RegistryView
from blockchain.components.transactions.transactions_view import  TransactionsView
from blockchain.views.mine import MineView
from blockchain.views.nodes import NewNodeView, RegisterNodeView, BlockSyncView

urlpatterns = [
    path("registry/", RegistryView.as_view()),
    path("registry/<int:id_>", RegistryView.as_view()),

    path("transaction/", TransactionsView.as_view()),
    
    path("mine/", MineView.as_view()),

    path("register_node/", NewNodeView.as_view()),
    path("register_with/", RegisterNodeView.as_view()),
    path("sync_block/", BlockSyncView.as_view()),

]