from rest_framework.response import Response
from rest_framework import status

from adapters.factory import DjangoStorageFactory
from blockchain.libraries.factory import LibraryFactory

from blockchain.src.registry.registry_service import RegistryService

class NodeService():
    
    def __init__(self, storage: DjangoStorageFactory, library: LibraryFactory):
        self.storage = storage
        self.library = library

    def new_node(self, payload: dict):
        addr = payload.get("node_address")
        
        if not addr:
            return Response({"message": "Missing node_address field!"}, status.HTTP_400_BAD_REQUEST)
        
        #TODO: COMUNICATE NEW NODE TO PEERS
        self.storage.createPeersModel().insert({ "ip_address": addr })
        return RegistryService(self.storage, self.library).list()
