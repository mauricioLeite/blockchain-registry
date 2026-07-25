from unittest.mock import patch

from django.test import TestCase
from requests.exceptions import ConnectionError as RequestsConnectionError

from adapters.factory import DjangoStorageFactory
from blockchain.libraries.factory import LibraryFactory
from blockchain.src.mine.mine_service import MineService


class MineServiceUnreachablePeerTests(TestCase):

    def setUp(self):
        self.storage = DjangoStorageFactory()
        self.library = LibraryFactory(self.storage)
        self.storage.createPeersModel().insert({"ip_address": "unreachable-peer:8080"})
        self.storage.createPendingTransactionsModel().insert({"transaction": {"a": 1}})

    @patch("blockchain.libraries.peers_manager.requests.post", side_effect=RequestsConnectionError("boom"))
    @patch("blockchain.libraries.peers_manager.requests.get", side_effect=RequestsConnectionError("boom"))
    def test_mine_succeeds_and_consumes_the_transaction_exactly_once(self, mock_get, mock_post):
        response = MineService(self.storage, self.library).mine()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["accepted"])

        second = MineService(self.storage, self.library).mine()
        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.data["message"], "No transaction available.")

        chain = self.library.createBlockchain().chain
        mined_transactions = [block["transaction"] for block in chain if block["index"] != 0]
        self.assertEqual(mined_transactions, [{"a": 1}])
