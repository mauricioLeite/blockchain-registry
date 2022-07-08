from typing import Union
import requests, json

from adapters.factory import DjangoStorageFactory

from ..libraries.blockchain import Blockchain
from ..libraries.peers_manager import PeersManager

class RegistryOperations:

    def __init__(self, blockchain: Blockchain, storage: DjangoStorageFactory = None, peers: PeersManager = None) -> None:
        self.__blockchain = blockchain
        self.storage = storage
        self.peers = peers

    def list(self, id_: Union[str, int] = None):
        print(self.__blockchain.chain)
        peers = self.peers.list()
        if id_:
            block = self.__blockchain.get_block(id_)
            return block, peers
        return self.__blockchain.chain, peers

    def insert_new_block(self, data: dict):
        self.__blockchain.add_new_transaction(data)
        return True
        
    def mine(self):
        unconfirmed_transaction = self.storage.createPendingTransactionsModel().first()
        mined_block_id = self.__blockchain.mine(unconfirmed_transaction)
        if not mined_block_id: return None

        chain_length = len(self.__blockchain.chain)
        # self.consensus()
        if chain_length == len(self.__blockchain.chain):
            self.announce_new_block(self.__blockchain.last_block)
            self.storage.createPendingTransactionsModel().delete({ "id": unconfirmed_transaction["id"] })
        
        return self.__blockchain.last_block

    
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

    def pending_transactions(self):
        return self.storage.createPendingTransactionsModel().get_all()