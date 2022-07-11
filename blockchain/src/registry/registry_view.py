import json, logging

from rest_framework.views import APIView

from adapters.factory import DjangoStorageFactory

from blockchain.src.registry.registry_service import RegistryService
from blockchain.libraries.factory import LibraryFactory

storage = DjangoStorageFactory()
library = LibraryFactory(storage)

class RegistryView(APIView):

    def get(self, _, id_ = None):
        payload = {"registry_id": id_}
        logging.info(json.dumps({ "class": "RegistryView" , "payload": payload }, ensure_ascii=False))
        
        return RegistryService(storage, library).list(id_)
