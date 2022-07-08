from typing import Union

from rest_framework.response import Response
from rest_framework import status

from adapters.factory import DjangoStorageFactory
from blockchain.libraries.factory import LibraryFactory

class RegistryService:

    def __init__(self, storage: DjangoStorageFactory, library: LibraryFactory) -> None:
        self.storage = storage
        self.library = library
        
    def list(self, id_: Union[str,int] = None):
        peers = self.library.createPeersManager().list()
        blockchain = self.library.createBlockchain()
        if id_:
            chain = blockchain.get_block(id_)
        else:
            chain = blockchain.chain
        return Response({"chain": chain, "peers": peers, "length": len(chain)}, status.HTTP_200_OK)

    