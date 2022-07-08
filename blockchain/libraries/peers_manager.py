import json
from adapters.factory import DjangoStorageFactory

class PeersManager:
    def __init__(self, storage: DjangoStorageFactory = None):
        self.storage = storage

    def list(self):
        peers = self.storage.createPeersModel().get_all()
        formatted = []
        for peer in peers:
            formatted.append(peer["ip_address"])
        return formatted

    def sync_peers(self, peers: list):
        for peer in peers:
            self.storage.createPeersModel().insert({ 'ip_address': peer })
        return True