import requests
import json
import { Response, HttpStatus } from '@nestjs/common';

import { DjangoStorageFactory } from '../adapters/factory/django-storage.factory';
import { LibraryFactory } from '../blockchain/libraries/factory/library.factory';
import { RegistryService } from '../blockchain/src/registry/registry.service';
import { Block } from '../blockchain/libraries/block/block';

export class NodeService {

    private storage: DjangoStorageFactory;
    private library: LibraryFactory;

    constructor(storage: DjangoStorageFactory, library: LibraryFactory) {
        this.storage = storage;
        this.library = library;
    }

    public async newNode(payload: { node_address: string }): Promise<Response> {
        const addr = payload.node_address;

        if (!addr) {
            return { message: 'Missing node_address field!' }, HttpStatus.BAD_REQUEST;
        }

        this.storage.createPeersModel().insert({ ip_address: addr });
        return new RegistryService(this.storage, this.library).list();
    }

    public async joinNetwork(payload: { node_address: string }, host: string): Promise<Response> {
        const addr = payload.node_address;

        if (!addr) {
            return { message: 'Missing node_address field!' }, HttpStatus.BAD_REQUEST;
        }

        const data = { node_address: host };
        const headers = { 'Content-Type': 'application/json' };

        const response = await requests.post(
            `http://${addr}/node/register`, { data, headers });

        if (response.statusCode === 200) {
            const responsePayload = response.json();
            this.library.createBlockchain().createChainFromDump(responsePayload.chain);
            this.library.createPeersManager().syncPeers([addr, ...responsePayload.peers], host);
            return { message: 'Registration successful' }, HttpStatus.OK;
        } else {
            return { message: 'Error registering node in network.' }, HttpStatus.INTERNAL_SERVER_ERROR;
        }
    }

    public async syncBlock(block: Block): Promise<Response> {
        const proof = block.hash;
        delete block.id;
        delete block.hash;
        delete block.createdAt;

        const added = this.library.createBlockchain().addBlock(block, proof);

        if (!added) {
            return { message: 'The block is discarded by the node.' }, HttpStatus.INTERNAL_SERVER_ERROR;
        }

        return { message: 'Block added to the chain' }, HttpStatus.CREATED;
    }

    public async clearLocal(): Promise<Response> {
        this.storage.createPeersModel().delete();
        this.storage.createBlockModels().delete();
        return { message: 'Clear complete!' }, HttpStatus.OK;
    }
}
