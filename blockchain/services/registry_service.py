import logging, json
from typing import Union

from rest_framework.response import Response
from rest_framework import status

from .registry_operations import RegistryOperations
class RegistryService:

    def __init__(self, operations: RegistryOperations) -> None:
        self.__operations = operations
        
    def list(self, id_: Union[str,int] = None):
        chain = self.__operations.list(id_)
        return Response({"chain": chain, "length": len(chain)}, status.HTTP_200_OK)

    def insert_registry(self, payload: dict) -> Response:
        confirm = self.__operations.insert_new_block(payload)
        if confirm:
            return Response({"message":"Transaction requested!"}, status.HTTP_201_CREATED)
        return Response({"message":"Internal Error"}, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def pending(self):
        pending_tx = self.__operations.pending_transactions()
        return Response({"unconfirmed_transactions": pending_tx, "length": len(pending_tx)}, status.HTTP_200_OK)

    def mine(self):
        chain = self.__operations.mine()
        return Response({"chain": chain, "length": len(chain)}, status.HTTP_200_OK)