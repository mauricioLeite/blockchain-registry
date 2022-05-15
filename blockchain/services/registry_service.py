from typing import Union

from rest_framework.response import Response
from rest_framework import status

from .registry_operations import RegistryOperations
class RegistryService:

    def __init__(self, operations: RegistryOperations, peers: list = None) -> None:
        self.__operations = operations
        self.__peers = peers
        
    def list(self, id_: Union[str,int] = None):
        chain = self.__operations.list(id_)
        return Response({"chain": chain, "peers": self.__peers, "length": len(chain)}, status.HTTP_200_OK)

    def insert_registry(self, payload: dict) -> Response:
        # TODO: Need validation on payload strucuture
        confirm = self.__operations.insert_new_block(payload)
        if confirm:
            return Response({"message":"Transaction requested!"}, status.HTTP_201_CREATED)
        return Response({"message":"Internal Error"}, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def pending(self):
        pending_tx = self.__operations.pending_transactions()
        return Response({"unconfirmed_transactions": pending_tx, "length": len(pending_tx)}, status.HTTP_200_OK)

    def mine(self):
        # TODO: verify existence of pending transactions
        block = self.__operations.mine()
        if not block: return Response({"message": "No transaction to mine."}, status.HTTP_200_OK)
        
        return Response({"block": block}, status.HTTP_200_OK)
