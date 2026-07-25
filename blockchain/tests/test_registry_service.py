from django.test import TestCase

from adapters.factory import DjangoStorageFactory
from blockchain.libraries.factory import LibraryFactory


class RegistryEndpointTests(TestCase):

    def setUp(self):
        # Accessing the blockchain once ensures the genesis block exists.
        LibraryFactory(DjangoStorageFactory()).createBlockchain()

    def test_registry_by_id_zero_returns_only_the_genesis_block(self):
        response = self.client.get("/registry/0")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["length"], 1)
        self.assertEqual(len(response.data["chain"]), 1)
        self.assertEqual(response.data["chain"][0]["index"], 0)

    def test_registry_by_a_missing_id_returns_an_empty_chain(self):
        response = self.client.get("/registry/99")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["length"], 0)
        self.assertEqual(response.data["chain"], [])

    def test_registry_without_an_id_returns_the_full_chain(self):
        response = self.client.get("/registry/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["length"], 1)


class ConsensusEndpointTests(TestCase):
    def test_consensus_with_no_peers_reports_no_change(self):
        response = self.client.get("/consensus/")

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["replaced"])
