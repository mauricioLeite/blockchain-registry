from rest_framework.response import Response
from rest_framework import status

from adapters.factory import DjangoStorageFactory
from blockchain.libraries.factory import LibraryFactory
from blockchain.libraries.serializers import BlockSerializer

class MineService():

    def __init__(self, storage: DjangoStorageFactory, library: LibraryFactory):
        self.storage = storage
        self.library = library

    def mine(self):
        transaction = self.storage.createPendingTransactionsModel().first()
        if not transaction: return Response({"message": "No transaction available."}, status.HTTP_200_OK)

        blockchain = self.library.createBlockchain()
        mined_block = blockchain.mine(transaction)
        if not mined_block: return Response({"message": "Error on mining process."}, status.HTTP_500_INTERNAL_SERVER_ERROR)

        peers = self.library.createPeersManager()
        replaced = peers.consensus(blockchain)

        if replaced:
            return Response({"block": BlockSerializer(blockchain.last_block).data, "accepted": False}, status.HTTP_200_OK)

        self.storage.createPendingTransactionsModel().delete({ "id": transaction["id"] })
        peers.announce_new_block(mined_block)

        return Response({"block": BlockSerializer(mined_block).data, "accepted": True}, status.HTTP_200_OK)
