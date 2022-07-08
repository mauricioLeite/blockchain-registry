import json, logging

from rest_framework.views import APIView


from ..services.registry_service import RegistryService

from blockchain.libraries.peers_manager import PeersManager
from ..libraries.blockchain import Blockchain
from adapters.factory import DjangoStorageFactory

factory = DjangoStorageFactory()
blockchain = Blockchain(factory)
peers = PeersManager(factory)

class TransactionsView(APIView):

    def get(self, _):        
        return RegistryService().pending()

    def post(self, request, id_=None):
        payload = request.data
        logging.info(json.dumps({ "payload": payload }, ensure_ascii=False))
        
        return RegistryService().insert_registry(payload)

