from rest_framework.response import Response
from rest_framework import status

from adapters.factory import DjangoStorageFactory
from blockchain.libraries.factory import LibraryFactory

class TransactionsService:

    def __init__(self, storage: DjangoStorageFactory) -> None:
        self.storage = storage
        
    def create(self, payload: dict) -> Response:
        # TODO: Need validation on payload strucuture
        inserted = self.storage.createPendingTransactionsModel().insert({ "transaction": payload })
        if inserted:
            return Response({"message":"Transaction requested!"}, status.HTTP_201_CREATED)
        return Response({"message":"Internal Error"}, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def pending(self):
        pending_tx = self.storage.createPendingTransactionsModel().get_all()
        return Response({"unconfirmed_transactions": pending_tx, "length": len(pending_tx)}, status.HTTP_200_OK)
        