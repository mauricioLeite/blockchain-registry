import json, logging

from rest_framework.views import APIView

from ..services.registry_service import RegistryService
from ..services.registry_operations import RegistryOperations

from ..libraries.blockchain import Blockchain
from adapters.factory import DjangoStorageFactory

factory = DjangoStorageFactory()
blockchain = Blockchain(factory)
peers = set()

# Blockchain Logic Endpoints
class RegistryView(APIView):

    def get(self, _, id_ = None):
        payload = {"registry_id": id_}
        logging.info(json.dumps({ "payload": payload }, ensure_ascii=False))
        
        operations = RegistryOperations(blockchain)
        return RegistryService(operations, peers).list(id_)

    def post(self, request, id_=None):
        payload = request.data
        logging.info(json.dumps({ "payload": payload }, ensure_ascii=False))
        
        operations = RegistryOperations(blockchain)
        return RegistryService(operations).insert_registry(payload)

class PendingView(APIView):

    def get(self, _):        
        operations = RegistryOperations(blockchain)
        return RegistryService(operations).pending()

class MineView(APIView):

    def get(self, _):
        operations = RegistryOperations(blockchain, peers)
        return RegistryService(operations).mine()

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

        peers.add(addr)

        operations = RegistryOperations(blockchain)
        return RegistryService(operations, peers).list()

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
        if not addr:
            return Response({"message": "Missing node_address field!"}, status.HTTP_400_BAD_REQUEST)

        data = {"node_address": url}
        headers = {'Content-Type': "application/json"}

        # Make a request to register with remote node and obtain information
        response = requests.post(f"http://{addr}/register_node/",
                                data=json.dumps(data), headers=headers)

        if response.status_code == 200:
            global blockchain
            global peers
            # update chain and the peers
            chain_dump = response.json()['chain']
            blockchain = self._create_chain_from_dump(chain_dump)

            remote_peers = response.json()['peers']
            remote_peers.remove(url)
            peers.update(remote_peers)
            peers.add(addr)
            return Response({"message":"Registration successful"}, status.HTTP_200_OK)
        else:
            # if something goes wrong, pass it on to the API response
            return Response({"message": response.content}, response.status_code)
    
    def _create_chain_from_dump(self, chain_dump):
        generated_blockchain = Blockchain()
        
        for idx, block_data in enumerate(chain_dump):
            if idx == 0:
                generated_blockchain.last_block.timestamp = block_data.get("timestamp")
                generated_blockchain.last_block.hash = block_data.get("hash")
            else:
                block = Block(block_data["index"],
                            block_data["transaction"],
                            block_data["timestamp"],
                            block_data["previous_hash"],
                            block_data["nonce"])
                proof = block_data['hash']
                added = generated_blockchain.add_block(block, proof)
                if not added:
                    raise Exception("The chain dump is tampered!!")
            
        return generated_blockchain

"""
    Sync new block on chain with another registered nodes
"""
class BlockSyncView(APIView):

    def post(self, request):
        payload = request.data
        logging.info(json.dumps({ "payload": payload, "class": "BlockSync"}, ensure_ascii=False))
        
        block = Block(payload.get("index"), payload.get("transaction"), payload.get("timestamp"), payload.get("previous_hash"), payload.get("nonce"))

        proof = payload.get("hash")
        added = blockchain.add_block(block, proof)

        if not added: return Response({"message":"The block is discarded by the node."}, status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Block added to the chain"}, status.HTTP_201_CREATED)
    
