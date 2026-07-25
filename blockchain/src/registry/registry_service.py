from typing import Union

from rest_framework.response import Response
from rest_framework import status

from adapters.factory import DjangoStorageFactory
from blockchain.libraries.factory import LibraryFactory
from blockchain.libraries.serializers import BlockSerializer

class RegistryService:

    def __init__(self, storage: DjangoStorageFactory, library: LibraryFactory) -> None:
        self.storage = storage
        self.library = library

    def list(self, id_: Union[str,int] = None):
        peers = self.library.createPeersManager().list()
        blockchain = self.library.createBlockchain()

        if id_ is not None:
            block = blockchain.get_block(id_)
            chain = [block] if block else []
        else:
            chain = blockchain.chain

        serialized = BlockSerializer(chain, many=True).data
        return Response({"chain": serialized, "peers": peers, "length": len(serialized)}, status.HTTP_200_OK)
