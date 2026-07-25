from django.test import SimpleTestCase

from blockchain.src.transactions.serializers import TransactionSerializer
from blockchain.src.nodes.serializers import NodeAddressSerializer, BlockSyncSerializer


class TransactionSerializerTests(SimpleTestCase):
    def test_rejects_non_object_or_empty_payloads(self):
        for payload in (None, [], "x", 1, {}, True):
            with self.subTest(payload=payload):
                serializer = TransactionSerializer(data=payload)
                self.assertFalse(serializer.is_valid())
                self.assertIn("non_field_errors", serializer.errors)

    def test_accepts_a_non_empty_object(self):
        serializer = TransactionSerializer(data={"from": "a", "to": "b", "amount": 10})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data, {"from": "a", "to": "b", "amount": 10})


class NodeAddressSerializerTests(SimpleTestCase):
    def test_rejects_a_bare_hostname_without_a_port(self):
        self.assertFalse(NodeAddressSerializer(data={"node_address": "example.com"}).is_valid())

    def test_rejects_a_missing_field(self):
        self.assertFalse(NodeAddressSerializer(data={}).is_valid())

    def test_accepts_a_host_port_pair(self):
        serializer = NodeAddressSerializer(data={"node_address": "node2:8080"})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["node_address"], "node2:8080")


class BlockSyncSerializerTests(SimpleTestCase):
    def _valid_payload(self):
        return {
            "index": 1,
            "transaction": {"a": 1},
            "previous_hash": "0" * 64,
            "nonce": 5,
            "hash": "00" + "a" * 62,
            "created_at": "2024-01-01T00:00:00.000000Z",
        }

    def test_accepts_a_well_formed_block(self):
        self.assertTrue(BlockSyncSerializer(data=self._valid_payload()).is_valid())

    def test_rejects_a_non_hex_hash(self):
        payload = self._valid_payload()
        payload["hash"] = "not-hex"
        self.assertFalse(BlockSyncSerializer(data=payload).is_valid())

    def test_rejects_the_genesis_index(self):
        payload = self._valid_payload()
        payload["index"] = 0
        self.assertFalse(BlockSyncSerializer(data=payload).is_valid())

    def test_rejects_an_unparseable_timestamp(self):
        payload = self._valid_payload()
        payload["created_at"] = "not-a-timestamp"
        self.assertFalse(BlockSyncSerializer(data=payload).is_valid())
