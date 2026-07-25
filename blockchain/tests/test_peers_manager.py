from unittest.mock import patch

from django.test import TestCase
from requests.exceptions import ConnectionError as RequestsConnectionError

from adapters.factory import DjangoStorageFactory
from blockchain.libraries.factory import LibraryFactory
from blockchain.libraries.serializers import BlockSerializer


class ConsensusTests(TestCase):
    def setUp(self):
        self.storage = DjangoStorageFactory()
        self.library = LibraryFactory(self.storage)
        self.storage.createPeersModel().insert({"ip_address": "peer:8080"})

    @patch("blockchain.libraries.peers_manager.requests.get", side_effect=RequestsConnectionError("boom"))
    def test_an_unreachable_peer_is_skipped_instead_of_raising(self, mock_get):
        blockchain = self.library.createBlockchain()
        replaced = self.library.createPeersManager().consensus(blockchain)
        self.assertFalse(replaced)

    @patch("blockchain.libraries.peers_manager.requests.get")
    def test_a_longer_valid_peer_chain_is_adopted(self, mock_get):
        blockchain = self.library.createBlockchain()
        blockchain.mine({"transaction": {"a": 1}})
        longer_chain = BlockSerializer(blockchain.chain, many=True).data

        # Roll back locally to just genesis, simulating a node that fell behind.
        self.storage.createBlockModels().delete({"index": (">", 0)})
        self.assertEqual(len(blockchain.chain), 1)

        mock_get.return_value.json.return_value = {"length": 2, "chain": longer_chain}

        replaced = self.library.createPeersManager().consensus(blockchain)

        self.assertTrue(replaced)
        self.assertEqual(len(blockchain.chain), 2)

    @patch("blockchain.libraries.peers_manager.requests.get")
    def test_a_shorter_or_equal_peer_chain_is_not_adopted(self, mock_get):
        blockchain = self.library.createBlockchain()
        blockchain.mine({"transaction": {"a": 1}})
        current_chain = BlockSerializer(blockchain.chain, many=True).data

        mock_get.return_value.json.return_value = {"length": len(current_chain), "chain": current_chain}

        replaced = self.library.createPeersManager().consensus(blockchain)

        self.assertFalse(replaced)


class AnnounceNewBlockTests(TestCase):
    def setUp(self):
        self.storage = DjangoStorageFactory()
        self.library = LibraryFactory(self.storage)
        self.storage.createPeersModel().insert({"ip_address": "unreachable-peer:8080"})

    @patch("blockchain.libraries.peers_manager.requests.post", side_effect=RequestsConnectionError("boom"))
    def test_an_unreachable_peer_does_not_raise(self, mock_post):
        blockchain = self.library.createBlockchain()
        mined = blockchain.mine({"transaction": {"a": 1}})
        # Must not raise, even though the only known peer is unreachable.
        self.library.createPeersManager().announce_new_block(mined)
