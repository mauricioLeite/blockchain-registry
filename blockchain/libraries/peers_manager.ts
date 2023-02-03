import { PeersModel } from "./adapters/factory";

export class PeersManager {
  storage: PeersModel;

  constructor(storage: PeersModel) {
    this.storage = storage;
  }

  list(): string[] {
    const peers = this.storage.getAll();
    const formatted: string[] = [];
    for (const peer of peers) {
      formatted.push(peer.ip_address);
    }
    return formatted;
  }

  syncPeers(peers: string[], host: string): boolean {
    for (const peer of peers) {
      if (peer !== host) {
        this.storage.insert({ ip_address: peer });
      }
    }
    return true;
  }
}
