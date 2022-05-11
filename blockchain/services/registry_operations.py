from typing import Union

from ..libraries.blockchain import Blockchain

class RegistryOperations:

    def __init__(self, blockchain: Blockchain) -> None:
        self.__blockchain = blockchain

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
        return self.__blockchain.chain[mined_block_id].__dict__
    
    def pending_transactions(self):
        return self.__blockchain.unconfirmed_transactions