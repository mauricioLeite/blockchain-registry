import requests, json

from rest_framework.response import Response
from rest_framework import status

from adapters.factory import DjangoStorageFactory
from blockchain.libraries.factory import LibraryFactory
from blockchain.src.registry.registry_service import RegistryService
from blockchain.libraries.block import Block

class NodeService():
    
    def __init__(self, storage: DjangoStorageFactory, library: LibraryFactory):
        self.storage = storage
        self.library = library

    def new_node(self, payload: dict):
        addr = payload.get("node_address")

        if not addr:
            return Response({"message": "Missing node_address field!"}, status.HTTP_400_BAD_REQUEST)
        
        #TODO: check if node exist before insert and communicate new nodes to peers
        self.storage.createPeersModel().insert({ "ip_address": addr })
        return RegistryService(self.storage, self.library).list()

    def join_network(self, payload: dict, host: str):
        addr = payload.get("node_address")
        if not addr:
            return Response({"message": "Missing node_address field!"}, status.HTTP_400_BAD_REQUEST)

        data = {"node_address": host}
        headers = {'Content-Type': "application/json"}

        # Make a request to register with remote node and obtain information
        response = requests.post(f"http://{addr}/node/register", data=json.dumps(data), headers=headers)
        if response.status_code == 200:
            payload = response.json()
            # update chain and the peers
            self.library.createBlockchain().create_chain_from_dump(payload['chain'])
            # #nesse nó ou em um novo nó DESENHAR!
            self.library.createPeersManager().sync_peers([addr, *payload['peers']], host)

            return Response({"message":"Registration successful"}, status.HTTP_200_OK)
        else:
            return Response({"message": "Error registering node in network."}, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def sync_block(self, block: dict):
        proof = block['hash']
        for key in ['id', 'hash', 'created_at']:
            if key in block: del block[key]

        block = Block(**block)
        added = self.library.createBlockchain().add_block(block, proof)

        if not added: return Response({"message":"The block is discarded by the node."}, status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Block added to the chain"}, status.HTTP_201_CREATED)

    #TODO: remove method after tests
    def clear_local(self):
        self.storage.createPeersModel().delete()
        self.storage.createBlockModels().delete()
        return  Response({"message": "Clear complete!"}, status.HTTP_200_OK)
        