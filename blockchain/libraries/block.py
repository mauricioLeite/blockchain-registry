import json
from hashlib import sha256

class Block:
    def __init__(self, index, transaction, timestamp, previous_hash, nonce=0, hash=None):
        self.index = index
        self.transaction = transaction
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = hash

    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()