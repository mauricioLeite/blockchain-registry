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
        logging.info(json.dumps({ "class": "NewNodeView" , "payload": payload }, ensure_ascii=False))
        return NodeService(storage, library).new_node(payload)

#TODO: remove class after tests
class ClearLocalPeers(APIView):

    def get(self, request):
        logging.info(json.dumps({ "class": "ClearLocalPeers" , "message": "Clear request received!" }, ensure_ascii=False))
        return NodeService(storage, library).clear_local()


from ...libraries.block import Block
# Join network based on reference node received
class JoinView(APIView):

    def post(self, request):
        payload = request.data
        host = request.get_host()
        logging.info(json.dumps({ "class": "JoinView", "payload": payload, "host": host }, ensure_ascii=False))
        return NodeService(storage, library).join_network(payload, host)
    
"""
    Sync new block on chain with another registered nodes
"""
class BlockSyncView(APIView):

    def post(self, request):
        payload = json.loads(request.data)
        logging.info(json.dumps({ "class": "BlockSync", "payload": payload}, ensure_ascii=False))
        return NodeService(storage, library).sync_block(payload)
        
    
