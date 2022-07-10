import time
from .block import Block

from adapters.factory import DjangoStorageFactory

class Blockchain: 
    difficulty = 2

    def __init__(self, factory: DjangoStorageFactory):
        self.storage = factory
        self.__create_genesis_block()
 
    def __create_genesis_block(self, reference: Block = None):
        blocks_model = self.storage.createBlockModels()
        if blocks_model.count_rows() == 0:
            if not reference:
                genesis_block = Block(0, [], time.time(), "0")
                genesis_block.hash = genesis_block.compute_hash()
            else:
                del reference["id"]
                genesis_block = Block(**reference)
            self.storage.createBlockModels().insert(genesis_block.__dict__)

    @property
    def chain(self):
        return self.storage.createBlockModels().get_all()
    
    @property
    def last_block(self):
        return self.storage.createBlockModels().last()
        
    def get_block(self, id_: int):
        block = self.storage.createBlockModels().get({"index": id_})
        return block if block else []

    #   NEW BLOCKS LOGIC
    def mine(self, unconfirmed_transaction: dict):
        del unconfirmed_transaction["created_at"]
        last_block = self.last_block
        
        new_block = Block(
            index=last_block["index"] + 1,
            transaction=unconfirmed_transaction,
            previous_hash=last_block["hash"]
        )

        proof = self.__proof_of_work(new_block)
        id_ = self.add_block(new_block, proof)
        return id_, unconfirmed_transaction["id"]


    def __proof_of_work(self, block: Block):
        # TODO: internalize nonce compute
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith("0" * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    def add_block(self, block, proof):
        previous_hash = self.last_block["hash"]
        if previous_hash != block.previous_hash:
            return False

        if not self.is_valid_proof(block, proof):
            return False

        block.hash = proof
        return self.storage.createBlockModels().insert(block.__dict__)
 
    def is_valid_proof(self, block, block_hash):
        return (block_hash.startswith("0" * Blockchain.difficulty) and
            block_hash == block.compute_hash())

    
    # CONSENSUS LOGIC
    '''
        Check if entire Blockchain is valid
    '''
    def check_chain_validity(self, chain: dict):
        previous_hash = self.get_block(0)["hash"]
        for idx, block in enumerate(chain):
            if block["index"] == 0: continue
            block_hash = block['hash']
            for key in ['id', 'hash', 'created_at']:
                del block[key]

            if not self.is_valid_proof(Block(**block), block_hash) or previous_hash != block['previous_hash']:
                return False
            block['hash'], previous_hash = block_hash, block_hash
        return True

    # Sync new node
    def create_chain_from_dump(self, chain_dump: dict):
        #TODO: implement chain rollback
        self.storage.createBlockModels().delete()
        
        for block_data in chain_dump:
            if block_data["index"] == 0:
                self.__create_genesis_block(block_data)
            else:
                proof = block_data['hash']
                for key in ['id', 'hash', 'created_at']:
                    if key in block_data: del block_data[key]

                block = Block(**block_data)
                added = self.add_block(block, proof)
                if not added:
                    raise Exception("The chain dump is tampered!!")
            
        return self.chain