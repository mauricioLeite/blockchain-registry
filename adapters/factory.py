from .orm.block_orm import BlocksORM
from .orm.pending_transactions_orm import PendingTransactionsORM

from .strategy import StrategyModel

class DjangoStorageFactory():
    def __init__(self) -> None:
        pass

    def createBlockModels(self) -> StrategyModel:
        return StrategyModel(BlocksORM)

    def createEntitiesModel(self) -> StrategyModel:
        return StrategyModel(PendingTransactionsORM)