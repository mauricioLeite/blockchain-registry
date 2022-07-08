import json, logging

from rest_framework.views import APIView


from ..services.registry_service import RegistryService
from ..services.registry_operations import RegistryOperations

from blockchain.libraries.peers_manager import PeersManager
from ..libraries.blockchain import Blockchain
from adapters.factory import DjangoStorageFactory

factory = DjangoStorageFactory()
blockchain = Blockchain(factory)
peers = PeersManager(factory)

class PendingView(APIView):

    def get(self, _):        
        operations = RegistryOperations(blockchain, storage=factory)
        return RegistryService(operations).pending()

class MineView(APIView):

    def get(self, _):
        operations = RegistryOperations(blockchain, factory)
        return RegistryService(operations).mine()
