import requests from "request";
import { Response, HttpStatus } from "./rest_framework";
import { PeersModel, PendingTransactionsModel, Blockchain } from "./adapters/factory";

export class MineService {
  storage: PeersModel & PendingTransactionsModel;
  library: Blockchain;

  constructor(storage: PeersModel & PendingTransactionsModel, library: Blockchain) {
    this.storage = storage;
    this.library = library;
  }

  mine(): Response {
    const transaction = this.storage.createPendingTransactionsModel().first();
    if (!transaction) {
      return {
        message: "No transaction available.",
        status: HttpStatus.OK,
      };
    }

    const blockchain = this.library.createBlockchain();
    const minedBlockId = blockchain.mine(transaction);
    if (!minedBlockId) {
      return {
        message: "Error on mining process.",
        status: HttpStatus.INTERNAL_SERVER_ERROR,
      };
    }

    const chainLength = blockchain.chain.length;
    this.consensus();
    if (chainLength === blockchain.chain.length) {
      this.announceNewBlock(blockchain.lastBlock);
      this.storage.createPendingTransactionsModel().delete({ id: transaction.id });
    }

    return {
      block: blockchain.lastBlock,
      status: HttpStatus.OK,
    };
  }

  consensus() {
    let longestChain = null;
    let currentLen = this.library.createBlockchain().chain.length;
    const peers = this.storage.createPeersModel().getAll();
    for (const node of peers) {
      const response = requests.get(`http://${node.ip_address}/registry`);
      const length = response.json().length;
      const chain = response.json().chain;
      if (length > currentLen && this.library.createBlockchain().checkChainValidity(chain)) {
        currentLen = length;
        longestChain = chain;
      }
    }
    if (longestChain) {
      this.library.createBlockchain().createChainFromDump(longestChain);
    }
  }

  announceNewBlock(block: object) {
    if ("created_at" in block) delete block["created_at"];
    const peers = this.storage.createPeersModel().getAll();
    for (const node of peers) {
      requests.post(`http://${node.ip_address}/node/sync_block`, {
        json: JSON.stringify(block),
      });
    }
  }
}
