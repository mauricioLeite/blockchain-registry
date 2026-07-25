from django.test import SimpleTestCase

from blockchain.models import Blocks, PendingTransactions, Peers
from adapters.orm.block_orm import BlocksORM
from adapters.orm.pending_transactions_orm import PendingTransactionsORM
from adapters.orm.peers_orm import PeersORM


class ModelOrmParityTests(SimpleTestCase):

    def _field_names(self, model):
        return {field.name for field in model._meta.get_fields()} - {"id"}

    def test_blocks_fields_match(self):
        self.assertEqual(self._field_names(Blocks), self._field_names(BlocksORM))

    def test_pending_transactions_fields_match(self):
        self.assertEqual(self._field_names(PendingTransactions), self._field_names(PendingTransactionsORM))

    def test_peers_fields_match(self):
        self.assertEqual(self._field_names(Peers), self._field_names(PeersORM))
