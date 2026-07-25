from django.test import TestCase

from adapters.factory import DjangoStorageFactory
from blockchain.libraries.blockchain import Blockchain
from blockchain.libraries.block import GENESIS_HASH

DIFFICULTY_PREFIX = "0" * Blockchain.difficulty


class BlockchainTests(TestCase):
    def setUp(self):
        self.storage = DjangoStorageFactory()
        self.blockchain = Blockchain(self.storage)

    def test_genesis_block_is_the_canonical_shared_genesis(self):
        genesis = self.blockchain.chain[0]
        self.assertEqual(genesis["hash"], GENESIS_HASH)
        self.assertEqual(genesis["previous_hash"], "0")

    def test_mine_produces_a_valid_proof_of_work(self):
        mined = self.blockchain.mine({"transaction": {"a": 1}})
        self.assertTrue(mined)
        self.assertTrue(mined["hash"].startswith(DIFFICULTY_PREFIX))
        self.assertEqual(mined["previous_hash"], GENESIS_HASH)

    def test_tampered_transaction_is_rejected(self):
        self.blockchain.mine({"transaction": {"a": 1}})
        chain = self.blockchain.chain
        chain[1]["transaction"] = {"a": "EVIL-REWRITE"}
        self.assertFalse(self.blockchain.check_chain_validity(chain))

    def test_check_chain_validity_does_not_mutate_its_input(self):
        self.blockchain.mine({"transaction": {"a": 1}})
        chain = self.blockchain.chain
        before = [dict(block) for block in chain]

        self.blockchain.check_chain_validity(chain)

        self.assertEqual(chain, before)

    def test_a_chain_with_a_foreign_genesis_is_rejected(self):
        self.blockchain.mine({"transaction": {"a": 1}})
        chain = self.blockchain.chain
        chain[0]["hash"] = "f" * 64
        self.assertFalse(self.blockchain.check_chain_validity(chain))

    def test_create_chain_from_dump_rejects_a_tampered_genesis(self):
        self.blockchain.mine({"transaction": {"a": 1}})
        dump = [dict(block) for block in self.blockchain.chain]
        dump[0]["hash"] = "f" * 64

        with self.assertRaises(Exception):
            self.blockchain.create_chain_from_dump(dump)

    def test_create_chain_from_dump_rolls_back_atomically_on_a_tampered_block(self):
        self.blockchain.mine({"transaction": {"a": 1}})
        good_dump = [dict(block) for block in self.blockchain.chain]

        tampered = [dict(block) for block in good_dump]
        tampered[1]["hash"] = "0" * 64  # well-formed hex, but not this block's proof

        with self.assertRaises(Exception):
            self.blockchain.create_chain_from_dump(tampered)

        # The local chain must survive intact, not be left half-deleted.
        current = self.blockchain.chain
        self.assertEqual(len(current), len(good_dump))
        self.assertEqual(current[-1]["hash"], good_dump[-1]["hash"])

    def test_create_chain_from_dump_accepts_a_valid_dump(self):
        self.blockchain.mine({"transaction": {"a": 1}})
        dump = [dict(block) for block in self.blockchain.chain]

        rebuilt = self.blockchain.create_chain_from_dump(dump)

        self.assertEqual(len(rebuilt), len(dump))
        self.assertEqual(rebuilt[-1]["hash"], dump[-1]["hash"])
