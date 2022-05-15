from typing import Union
import requests, json

from ..libraries.blockchain import Blockchain

class RegistryOperations:

    def __init__(self, blockchain: Blockchain, peers: list = None) -> None:
        self.__blockchain = blockchain
        self.__peers = peers

    def list(self, id_: Union[str, int] = None):
        if id_:
            return [self.__blockchain.chain[id_].__dict__]

        chain = []
        for block in self.__blockchain.chain:
            chain.append(block.__dict__)
        return chain

    def insert_new_block(self, data: dict):
        self.__blockchain.add_new_transaction(data)
        return True
        
    def mine(self):
        mined_block_id = self.__blockchain.mine()
        if not mined_block_id: return None

        chain_length = len(self.__blockchain.chain)
        self.consensus()
        if chain_length == len(self.__blockchain.chain):
            self.announce_new_block(self.__blockchain.last_block)
        
        return self.__blockchain.last_block.__dict__

    
    def consensus(self):
        """
        Our simple consensus algorithm. If a longer valid chain is
        found, our chain is replaced with it.
        """
        longest_chain = None
        current_len = len(self.__blockchain.chain)
        for node in self.__peers:
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
        for peer in self.__peers:
            requests.post(f"http://{peer}/sync_block/", json=block.__dict__)



    def pending_transactions(self):
        return self.__blockchain.unconfirmed_transactions