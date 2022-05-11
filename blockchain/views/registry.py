import json, logging

from rest_framework.views import APIView

from ..services.registry_service import RegistryService
from ..services.registry_operations import RegistryOperations

from ..libraries.blockchain import Blockchain

blockchain = Blockchain()

class RegistryView(APIView):

    def get(self, request, id_ = None):
        payload = {"registry_id": id_}
        logging.info(json.dumps({ "payload": payload }, ensure_ascii=False))
        
        operations = RegistryOperations(blockchain)
        return RegistryService(operations).list(id_)

    def post(self, request, id_=None):
        payload = request.data
        logging.info(json.dumps({ "payload": payload }, ensure_ascii=False))
        
        operations = RegistryOperations(blockchain)
        return RegistryService(operations).insert_registry(payload)

    # def patch(self, request, id_):
    #     payload = { "id": id_, **request.data }
    #     logging.info(json.dumps({ "payload": payload }, ensure_ascii=False))
        
    #     return RegistryService()

    # def delete(self, request, id_=None):
    #     payload = request.data
    #     logging.info(json.dumps({ "payload": payload }, ensure_ascii=False))
        
    #     return RegistryService()

class PendingView(APIView):

    def get(self, request):        
        operations = RegistryOperations(blockchain)
        return RegistryService(operations).pending()

class MineView(APIView):

    def get(self, request):
        operations = RegistryOperations(blockchain)
        return RegistryService(operations).mine()

