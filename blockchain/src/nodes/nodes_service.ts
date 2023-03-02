import requests
import json
import { Response, HttpStatus } from '@nestjs/common';

import { DjangoStorageFactory } from '../adapters/factory/django-storage.factory';
import { LibraryFactory } from '../blockchain/libraries/factory/library.factory';
import { RegistryService } from '../blockchain/src/registry/registry.service';
import { Block } from '../blockchain/libraries/block/block';

// Classe que lida com comunicação e armazenamento de dados relacionados à blockchain
export class NodeService {

    private storage: DjangoStorageFactory;
    private library: LibraryFactory;

    constructor(storage: DjangoStorageFactory, library: LibraryFactory) {
        this.storage = storage;
        this.library = library;
    }

    /*
    Verifica se o endereço do novo nó está presente e, em caso afirmativo, adiciona o novo nó ao armazenamento de pares (peers) e retorna a lista de pares atualizada
    */
    public async newNode(payload: { node_address: string }): Promise<Response> {
        const addr = payload.node_address;

        if (!addr) {
            return { message: 'Missing node_address field!' }, HttpStatus.BAD_REQUEST;
        }

        this.storage.createPeersModel().insert({ ip_address: addr });
        return new RegistryService(this.storage, this.library).list();
    }

    /*
    Verifica se o endereço do novo nó está presente e, em caso afirmativo, envia uma solicitação POST para o endereço especificado para registrar o novo nó
    */
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

    /*
    Tenta adicionar um bloco à cadeia de blocos
    */
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

    /*
     Limpa o armazenamento local de pares e blocos
    */
    public async clearLocal(): Promise<Response> {
        this.storage.createPeersModel().delete();
        this.storage.createBlockModels().delete();
        return { message: 'Clear complete!' }, HttpStatus.OK;
    }
}
