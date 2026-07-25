from django.db.transaction import atomic

from .block import Block, genesis_block, GENESIS_HASH

from adapters.factory import DjangoStorageFactory

class Blockchain:
    difficulty = 2

    def __init__(self, factory: DjangoStorageFactory):
        self.storage = factory
        self.__create_genesis_block()

    def __create_genesis_block(self, reference: dict = None):
        blocks_model = self.storage.createBlockModels()
        if blocks_model.count_rows() == 0:
            if reference and reference.get("hash") != GENESIS_HASH:
                raise Exception("The chain dump is tampered!! (invalid genesis block)")

            new_genesis = genesis_block()
            new_genesis.hash = GENESIS_HASH
            self.storage.createBlockModels().insert(new_genesis.__dict__)

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
        last_block = self.last_block

        new_block = Block(
            index=last_block["index"] + 1,
            transaction=unconfirmed_transaction.get("transaction"),
            previous_hash=last_block["hash"]
        )

        proof = self.__proof_of_work(new_block)
        return self.add_block(new_block, proof)

    #TODO: pass block as dict as parameter
    def __proof_of_work(self, block: Block):
        # TODO: internalize nonce compute
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith("0" * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    #TODO: pass block as dict as parameter
    def add_block(self, block: Block, proof: str):
        previous_hash = self.last_block["hash"]
        if previous_hash != block.previous_hash:
            return False

        if not self.is_valid_proof(block, proof):
            return False

        block.hash = proof
        return self.storage.createBlockModels().insert(block.__dict__)

    def is_valid_proof(self, block: Block, block_hash: str):
        return (block_hash.startswith("0" * Blockchain.difficulty) and
            block_hash == block.compute_hash())


    # CONSENSUS LOGIC
    '''
        Check if entire Blockchain is valid.
    '''
    def check_chain_validity(self, chain: list) -> bool:
        previous_hash = GENESIS_HASH
        for block in chain:
            block_hash = block.get('hash')

            if block['index'] == 0:
                if block_hash != GENESIS_HASH:
                    return False
                previous_hash = GENESIS_HASH
                continue

            payload = {k: v for k, v in block.items() if k not in ('id', 'hash')}
            if not self.is_valid_proof(Block(**payload), block_hash) or previous_hash != payload['previous_hash']:
                return False
            previous_hash = block_hash
        return True

    # Sync new node
    def create_chain_from_dump(self, chain_dump: list):
        with atomic():
            self.storage.createBlockModels().delete()

            for block_data in chain_dump:
                if block_data["index"] == 0:
                    self.__create_genesis_block(block_data)
                else:
                    proof = block_data['hash']
                    payload = {k: v for k, v in block_data.items() if k not in ('id', 'hash')}

                    block = Block(**payload)
                    added = self.add_block(block, proof)
                    if not added:
                        raise Exception("The chain dump is tampered!!")

            return self.chain
