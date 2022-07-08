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

# Blockchain Logic Endpoints
class RegistryView(APIView):

    def get(self, _, id_ = None):
        payload = {"registry_id": id_}
        logging.info(json.dumps({ "payload": payload }, ensure_ascii=False))
        
        operations = RegistryOperations(blockchain, peers=peers)
        return RegistryService(operations, factory).list(id_)

    def post(self, request, id_=None):
        payload = request.data
        logging.info(json.dumps({ "payload": payload }, ensure_ascii=False))
        
        operations = RegistryOperations(blockchain, storage=factory, peers=peers)
        return RegistryService(operations).insert_registry(payload)
