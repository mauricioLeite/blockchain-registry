import json, logging

from rest_framework.views import APIView

from adapters.factory import DjangoStorageFactory
from blockchain.src.transactions.transactions_service import TransactionsService

storage = DjangoStorageFactory()

class TransactionsView(APIView):
    def get(self, _):        
        return TransactionsService(storage).pending()

    def post(self, request, id_=None):
        payload = request.data
        logging.info(json.dumps({ "class": "TransactionsView" , "payload": payload }, ensure_ascii=False))
        
        return TransactionsService(storage).create(payload)

