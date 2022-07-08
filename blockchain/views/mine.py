import json, logging

from rest_framework.views import APIView


from ..components.registry.registry_service import RegistryService

from blockchain.libraries.peers_manager import PeersManager
from ..libraries.blockchain import Blockchain
from adapters.factory import DjangoStorageFactory

factory = DjangoStorageFactory()
blockchain = Blockchain(factory)
peers = PeersManager(factory)

class MineView(APIView):

    def get(self, _):
        return RegistryService().mine()
