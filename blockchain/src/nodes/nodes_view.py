import json, logging

from rest_framework.views import APIView

from adapters.factory import DjangoStorageFactory
from blockchain.libraries.factory import LibraryFactory
from blockchain.src.nodes.nodes_service import NodeService

storage = DjangoStorageFactory()
library = LibraryFactory(storage)

# TODO: Test all code below :\ 
from rest_framework.response import Response
from rest_framework import status

# Register external node on network
class NewNodeView(APIView):

    def post(self, request):
        payload = request.data
        logging.info(json.dumps({ "payload": payload }, ensure_ascii=False))
        return NodeService(storage, library).new_node(payload)

#TODO: remove class after tests
class ClearLocalPeers(APIView):

    def get(self, request):
        logging.info(json.dumps({ "message": "Clear request received!" }, ensure_ascii=False))
        return NodeService(storage, library).clear_local()


from ...libraries.block import Block
# Joinf network based on reference node received
class JoinView(APIView):

    def post(self, request):
        payload = request.data
        host = request.get_host()
        logging.info(json.dumps({ "payload": payload, "host": host }, ensure_ascii=False))
        return NodeService(storage, library).join_network(payload, host)
    
"""
    Sync new block on chain with another registered nodes
"""
class BlockSyncView(APIView):

    def post(self, request):
        payload = request.data
        logging.info(json.dumps({ "payload": payload, "class": "BlockSync"}, ensure_ascii=False))
        
        block = Block(payload.get("index"), payload.get("transaction"), payload.get("created_at"), payload.get("previous_hash"), payload.get("nonce"))

        proof = payload.get("hash")
        added = blockchain.add_block(block, proof)

        if not added: return Response({"message":"The block is discarded by the node."}, status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Block added to the chain"}, status.HTTP_201_CREATED)
    
