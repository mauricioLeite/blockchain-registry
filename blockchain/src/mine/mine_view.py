import json, logging
from django.http import HttpRequest
from rest_framework.views import APIView

from adapters.factory import DjangoStorageFactory
from blockchain.libraries.factory import LibraryFactory
from blockchain.src.mine.mine_service import MineService

storage = DjangoStorageFactory()
library = LibraryFactory(storage)

class MineView(APIView):

    def get(self, request: HttpRequest):
        logging.info(json.dumps({ "class": "ClearLocalPeers" , "message": "Mining request." }, ensure_ascii=False))
        return MineService(storage, library).mine()
