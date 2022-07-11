from django.urls import path 

from blockchain.src.registry.registry_view import RegistryView
from blockchain.src.transactions.transactions_view import  TransactionsView
from blockchain.src.mine.mine_view import MineView
from blockchain.src.nodes.nodes_view import NewNodeView, JoinView, BlockSyncView, ClearLocalPeers

urlpatterns = [
    path("registry/", RegistryView.as_view()),
    path("registry/<int:id_>", RegistryView.as_view()),

    path("transaction/", TransactionsView.as_view()),
    
    path("mine/", MineView.as_view()),

    path("node/register", NewNodeView.as_view()),
    path("node/join", JoinView.as_view()),
    path("node/sync_block", BlockSyncView.as_view()),

    #TODO: remove path after tests
    path("clear_peers/", ClearLocalPeers.as_view()),
]