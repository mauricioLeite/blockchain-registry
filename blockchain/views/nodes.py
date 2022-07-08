import json, logging

from rest_framework.views import APIView


from ..components.registry.registry_service import RegistryService

from blockchain.libraries.peers_manager import PeersManager
from ..libraries.blockchain import Blockchain
from adapters.factory import DjangoStorageFactory

factory = DjangoStorageFactory()
blockchain = Blockchain(factory)
peers = PeersManager(factory)

# TODO: Test all code below :\ 
from rest_framework.response import Response
from rest_framework import status
# Nodes Logic Endpoints
"""
    Register external node on existing network
"""
class NewNodeView(APIView):

    def post(self, request):
        payload = request.data
        logging.info(json.dumps({ "payload": payload }, ensure_ascii=False))

        addr = payload.get("node_address")
        if not addr:
            return Response({"message": "Missing node_address field!"}, status.HTTP_400_BAD_REQUEST)
        
        #TODO: COMUNICATE NEW NODE TO PEERS
        factory.createPeersModel().insert({ "ip_address": addr })
        print(payload)
        return RegistryService(operations, factory).list()

import requests
from ..libraries.block import Block
"""
    Internally calls the `register_node` endpoint to
    register current node with the remote node specified in the
    request, and sync the blockchain as well with the remote node.
"""
class RegisterNodeView(APIView):

    def post(self, request):
        url = request.get_host()
        payload = request.data
        logging.info(json.dumps({ "payload": payload, "url": url }, ensure_ascii=False))

        addr = payload.get("node_address")
        # if not addr:
        #     return Response({"message": "Missing node_address field!"}, status.HTTP_400_BAD_REQUEST)

        data = {"node_address": url}
        headers = {'Content-Type': "application/json"}

        # Make a request to register with remote node and obtain information
        # response = requests.post(f"http://{addr}/register_node/", data=json.dumps(data), headers=headers)
        #TODO: ADJUST TO SUPPORT DATABASE
        # if response.status_code == 200:
        if 200 == 200:
            # update chain and the peers
            blockchain.create_chain_from_dump(payload['chain'])
            #nesse nó ou em um novo nó DESENHAR!
            peers.sync_peers([addr, *payload['peers']])

            return Response({"message":"Registration successful"}, status.HTTP_200_OK)
        else:
            # if something goes wrong, pass it on to the API response
            # return Response({"message": response.content}, response.status_code)
            return Response({"message": "hy"}, 400)
    
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
    
