import json, logging

import requests
from requests.exceptions import RequestException

from adapters.factory import DjangoStorageFactory
from .serializers import BlockSerializer

class PeersManager:
    def __init__(self, storage: DjangoStorageFactory = None):
        self.storage = storage

    def list(self):
        peers = self.storage.createPeersModel().get_all()
        return [peer["ip_address"] for peer in peers]

    def sync_peers(self, peers: list, host: str):
        for peer in peers:
            if peer != host:
                self.storage.createPeersModel().insert({ 'ip_address': peer })
        return True

    def consensus(self, blockchain) -> bool:
        current_len = len(blockchain.chain)
        longest_chain = None

        for node in self.storage.createPeersModel().get_all():
            address = node['ip_address']
            try:
                response = requests.get(f"http://{address}/registry/", timeout=5)
                response.raise_for_status()
                payload = response.json()
            except (RequestException, ValueError) as error:
                logging.warning(json.dumps({"peer": address, "error": str(error)}, ensure_ascii=False))
                continue

            length, chain = payload.get('length'), payload.get('chain')
            if length and chain and length > current_len and blockchain.check_chain_validity(chain):
                current_len, longest_chain = length, chain

        if longest_chain:
            blockchain.create_chain_from_dump(longest_chain)
            return True
        return False

    def announce_new_block(self, block: dict):
        payload = BlockSerializer(block).data
        for node in self.storage.createPeersModel().get_all():
            address = node['ip_address']
            try:
                requests.post(f"http://{address}/node/sync_block", json=payload, timeout=5)
            except RequestException as error:
                logging.warning(json.dumps({"peer": address, "error": str(error)}, ensure_ascii=False))
