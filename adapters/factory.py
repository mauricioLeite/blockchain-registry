from .orm.block_orm import BlocksORM
from .orm.pending_transactions_orm import PendingTransactionsORM
from .orm.peers_orm import PeersORM

from .strategy import StrategyModel

class DjangoStorageFactory():
    def __init__(self) -> None:
        pass

    def createBlockModels(self) -> StrategyModel:
        return StrategyModel(BlocksORM)

    def createPendingTransactionsModel(self) -> StrategyModel:
        return StrategyModel(PendingTransactionsORM)

    def createPeersModel(self) -> StrategyModel:
        return StrategyModel(PeersORM)