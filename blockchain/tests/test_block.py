from datetime import datetime, timezone

from django.test import SimpleTestCase

from blockchain.libraries.block import Block, canonical_timestamp, genesis_block, GENESIS_HASH


class GenesisBlockTests(SimpleTestCase):

    def test_two_freshly_built_genesis_blocks_hash_identically(self):
        first = genesis_block()
        second = genesis_block()
        self.assertEqual(first.compute_hash(), second.compute_hash())
        self.assertEqual(first.compute_hash(), GENESIS_HASH)

    def test_genesis_hash_is_reproducible_from_its_own_fields(self):
        block = genesis_block()
        block.hash = block.compute_hash()
        self.assertEqual(block.hash, block.compute_hash())

    def test_genesis_previous_hash_is_not_a_timestamp(self):
        self.assertEqual(genesis_block().previous_hash, "0")


class CanonicalTimestampTests(SimpleTestCase):

    def test_pads_zero_microseconds(self):
        value = datetime(2024, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc)
        self.assertEqual(canonical_timestamp(value), "2024-01-01T00:00:00.000000Z")

    def test_naive_datetimes_are_treated_as_utc(self):
        naive = datetime(2024, 1, 1, 12, 30, 45, 123456)
        aware = naive.replace(tzinfo=timezone.utc)
        self.assertEqual(canonical_timestamp(naive), canonical_timestamp(aware))

    def test_a_block_hash_is_stable_across_a_string_round_trip(self):
        original = Block(index=1, transaction={"a": 1}, previous_hash="0" * 64)
        rendered = canonical_timestamp(original.created_at)
        rebuilt = Block(index=1, transaction={"a": 1}, previous_hash="0" * 64, created_at=rendered)
        self.assertEqual(original.compute_hash(), rebuilt.compute_hash())
