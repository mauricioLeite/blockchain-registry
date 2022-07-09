import requests

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
        print(f"block id: {mined_block_id}")
        if not mined_block_id: return  Response({"message": "Error on mining process."}, status.HTTP_500_INTERNAL_SERVER_ERROR)

        chain_length = len(blockchain.chain)
        # self.consensus()
        if chain_length == len(blockchain.chain):
            # self.announce_new_block(blockchain.last_block)
            self.storage.createPendingTransactionsModel().delete({ "id": transaction["id"] })
        block = blockchain.last_block
        return Response({"block": block}, status.HTTP_200_OK)

    #TODO: implements nodes communication on library
    def consensus(self):
        """
        Our simple consensus algorithm. If a longer valid chain is
        found, our chain is replaced with it.
        """
        longest_chain = None
        current_len = len(self.__blockchain.chain)
        peers = self.storage.createPeersModel().get_all()
        for _, node in peers.items():
            response = requests.get(f"http://{node}/registry")
            length = response.json()['length']
            chain = response.json()['chain']
            if length > current_len and self.__blockchain.check_chain_validity(chain):
                # Longer valid chain found!
                current_len = length
                longest_chain = chain
        if longest_chain:
            self.__blockchain = longest_chain
            return True

        return False

    def announce_new_block(self, block):
        """
        A function to announce to the network once a block has been mined.
        Other blocks can simply verify the proof of work and add it to their
        respective chains.
        """
        peers = self.storage.createPeersModel().get_all()
        for _, node in peers.items():
            requests.post(f"http://{node}/sync_block/", json=block)