import requests, json
from rest_framework.response import Response
from rest_framework import status
from adapters.factory import DjangoStorageFactory
from blockchain.libraries.factory import LibraryFactory

class MineService():
    
    def __init__(self, storage: DjangoStorageFactory, library: LibraryFactory):
        self.storage = storage
        self.library = library

    def mine(self):
        transaction = self.storage.createPendingTransactionsModel().first()
        if not transaction: return Response({"message": "No transaction available."}, status.HTTP_200_OK)
        
        blockchain = self.library.createBlockchain()
        mined_block_id = blockchain.mine(transaction)
        if not mined_block_id: return  Response({"message": "Error on mining process."}, status.HTTP_500_INTERNAL_SERVER_ERROR)

        chain_length = len(blockchain.chain)
        self.consensus()
        if chain_length == len(blockchain.chain):
            self.__announce_new_block(blockchain.last_block)
            self.storage.createPendingTransactionsModel().delete({ "id": transaction["id"] })

        return Response({"block": blockchain.last_block}, status.HTTP_200_OK)

    #TODO: implements nodes communication on library
    def consensus(self):
        longest_chain = None
        current_len = len(self.library.createBlockchain().chain)
        peers = self.storage.createPeersModel().get_all()
        for node in peers:
            response = requests.get(f"http://{node['ip_address']}/registry")
            length = response.json()['length']
            chain = response.json()['chain']
            if length > current_len and self.library.createBlockchain().check_chain_validity(chain):
                # Longer valid chain found!
                current_len = length
                longest_chain = chain
        if longest_chain:
            self.library.createBlockchain().create_chain_from_dump(longest_chain)

        return 

    def __announce_new_block(self, block: dict):
        if 'created_at' in block: del block['created_at']
        peers = self.storage.createPeersModel().get_all()
        for node in peers:
            requests.post(f"http://{node['ip_address']}/node/sync_block", json=json.dumps(block))