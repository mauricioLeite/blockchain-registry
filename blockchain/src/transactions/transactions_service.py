from rest_framework.response import Response
from rest_framework import status

from adapters.factory import DjangoStorageFactory
from blockchain.libraries.factory import LibraryFactory
from blockchain.src.transactions.serializers import TransactionSerializer

class TransactionsService:

    def __init__(self, storage: DjangoStorageFactory) -> None:
        self.storage = storage

    def create(self, payload: dict) -> Response:
        serializer = TransactionSerializer(data=payload)
        if not serializer.is_valid():
            return Response({"message": "Invalid transaction payload.", "errors": serializer.errors}, status.HTTP_400_BAD_REQUEST)

        inserted = self.storage.createPendingTransactionsModel().insert({ "transaction": serializer.validated_data })
        if inserted:
            return Response({"message":"Transaction requested!"}, status.HTTP_201_CREATED)
        return Response({"message":"Internal Error"}, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def pending(self):
        pending_tx = self.storage.createPendingTransactionsModel().get_all()
        return Response({"unconfirmed_transactions": pending_tx, "length": len(pending_tx)}, status.HTTP_200_OK)
