from .block import Block
from .blockchain import Blockchain
from .peers_manager import PeersManager

from adapters.factory import DjangoStorageFactory

class LibraryFactory():
    def __init__(self, storage: DjangoStorageFactory = None) -> None:
        self.storage = storage

    #TODO: possible delete Block class
    # def createBlock(self) -> Block():
    #     return Block()

    def createBlockchain(self) -> Blockchain:
        return Blockchain(self.storage)

    def createPeersManager(self) -> PeersManager:
        return PeersManager(self.storage)