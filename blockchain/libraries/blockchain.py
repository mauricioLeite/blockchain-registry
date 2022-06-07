import time
from .block import Block

from adapters.factory import DjangoStorageFactory

class Blockchain: 
    difficulty = 2

    def __init__(self, factory: DjangoStorageFactory):
        self.storage = factory
        self.unconfirmed_transactions = []
        # self.chain = []
        self.__create_genesis_block()
 
    def __create_genesis_block(self):
        blocks_model = self.storage.createBlockModels()
        if blocks_model.count_rows() == 0:
            genesis_block = Block(0, [], time.time(), "0")
            genesis_block.hash = genesis_block.compute_hash()
            self.storage.createBlockModels().insert(genesis_block)

    @property
    def chain(self):
        return self.storage.createBlockModels().get_all()
    
    @property
    def get_block(self, id_):
        return self.storage.createBlockModels().get({"id": id_})

    @property
    def last_block(self):
        return Block(**self.storage.createBlockModels().last())

    #   NEW BLOCKS LOGIC
    def proof_of_work(self, block):
        # TODO: internalize nonce compute
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith("0" * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    def add_block(self, block, proof):
        previous_hash = self.last_block.hash
        if previous_hash != block.previous_hash:
            return False
        if not self.is_valid_proof(block, proof):
            return False
        block.hash = proof
        return self.storage.createBlockModels().insert(block)
 
    def is_valid_proof(self, block, block_hash):
        return (block_hash.startswith("0" * Blockchain.difficulty) and
            block_hash == block.compute_hash())

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)
 
    def mine(self):
        if not self.unconfirmed_transactions:
            return False
 
        last_block = self.last_block
        new_block = Block(index=last_block.index + 1,
                          transaction=self.unconfirmed_transactions[0],
                          previous_hash=last_block.hash)
 
        proof = self.proof_of_work(new_block)
        id_ = self.add_block(new_block, proof)
        self.unconfirmed_transactions = self.unconfirmed_transactions[1:]
        return id_
        
    # CONSENSUS LOGIC
    '''
        Check if entire Blockchain is valid
    '''
    def check_chain_validy(cls, chain):
        result = True
        previous_hash = "0"

        for block in chain:
            block_hash = block.hash
            delattr(block, "hash")

            if not cls.is_valid_proof(block, block_hash) or previous_hash != block.previous_hash:
                return False
                               
            block.hash, previous_hash = block_hash, block_hash

        return result
