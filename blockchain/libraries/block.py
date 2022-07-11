import json
from hashlib import sha256

class Block:
    def __init__(self, index, transaction, previous_hash, created_at = None, nonce=0, hash=None, **kwargs):
        self.index = index
        self.transaction = transaction
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = hash
        self.created_at = created_at

    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()