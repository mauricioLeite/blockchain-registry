import logging, json

import requests
from requests.exceptions import RequestException

from rest_framework.response import Response
from rest_framework import status

from adapters.factory import DjangoStorageFactory
from blockchain.libraries.factory import LibraryFactory
from blockchain.libraries.block import Block
from blockchain.libraries.serializers import BlockSerializer
from blockchain.src.registry.registry_service import RegistryService
from blockchain.src.nodes.serializers import NodeAddressSerializer, BlockSyncSerializer

class NodeService():

    def __init__(self, storage: DjangoStorageFactory, library: LibraryFactory):
        self.storage = storage
        self.library = library

    def new_node(self, payload: dict):
        serializer = NodeAddressSerializer(data=payload)
        if not serializer.is_valid():
            return Response({"message": "Invalid node_address.", "errors": serializer.errors}, status.HTTP_400_BAD_REQUEST)
        addr = serializer.validated_data["node_address"]

        #TODO: check if node exist before insert and communicate new nodes to peers
        self.storage.createPeersModel().insert({ "ip_address": addr })
        return RegistryService(self.storage, self.library).list()

    def join_network(self, payload: dict, host: str):
        serializer = NodeAddressSerializer(data=payload)
        if not serializer.is_valid():
            return Response({"message": "Invalid node_address.", "errors": serializer.errors}, status.HTTP_400_BAD_REQUEST)
        addr = serializer.validated_data["node_address"]

        # Make a request to register with remote node and obtain information
        try:
            response = requests.post(f"http://{addr}/node/register", json={"node_address": host}, timeout=5)
        except RequestException as error:
            logging.error(json.dumps({"peer": addr, "error": str(error)}, ensure_ascii=False))
            return Response({"message": "Error registering node in network."}, status.HTTP_500_INTERNAL_SERVER_ERROR)

        if not response.ok:
            return Response({"message": "Error registering node in network."}, status.HTTP_500_INTERNAL_SERVER_ERROR)

        remote = response.json()
        # update chain and the peers
        self.library.createBlockchain().create_chain_from_dump(remote['chain'])
        self.library.createPeersManager().sync_peers([addr, *remote['peers']], host)

        return Response({"message":"Registration successful"}, status.HTTP_200_OK)

    def sync_block(self, block: dict):
        serializer = BlockSyncSerializer(data=block)
        if not serializer.is_valid():
            return Response({"message": "Invalid block payload.", "errors": serializer.errors}, status.HTTP_400_BAD_REQUEST)

        proof = serializer.validated_data.pop('hash')
        new_block = Block(**serializer.validated_data)
        added = self.library.createBlockchain().add_block(new_block, proof)

        if not added: return Response({"message":"The block is discarded by the node."}, status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Block added to the chain"}, status.HTTP_201_CREATED)

    def consensus(self):
        blockchain = self.library.createBlockchain()
        replaced = self.library.createPeersManager().consensus(blockchain)
        message = "Chain replaced by a longer valid chain." if replaced else "Current chain is already the longest valid chain."
        return Response({
            "message": message,
            "replaced": replaced,
            "chain": BlockSerializer(blockchain.chain, many=True).data,
        }, status.HTTP_200_OK)

    #TODO: remove method after tests
    def clear_local(self):
        self.storage.createPeersModel().delete()
        self.storage.createBlockModels().delete()
        return  Response({"message": "Clear complete!"}, status.HTTP_200_OK)
