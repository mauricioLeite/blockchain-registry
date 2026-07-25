# Blockchain API
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg?logo=python&logoColor=white)](https://www.python.org/downloads/release/python-3812/) [![Docker 20.10.17](https://img.shields.io/badge/docker-20.10.17-blue.svg?logo=docker&logoColor=white)](https://www.docker.com/) [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Simple Blockchain implementation using as cryptographic proof the Proof-of-Work (PoW) and as consensus the longest valid chain.

## Prerequisites
   - Docker should be installed (version 20.10.17 is used on tests).
   - Docker Compose should be installed (version 1.29.2 is used on tests).

## Running

After clone the repository, create a .env file based on .env.example and use your ip address as `BLOCKCHAIN_HOST`. `BLOCKCHAIN_HOST` accepts a comma-separated list, so a node can be reachable under more than one name at once (e.g. its container DNS alias and `localhost`). `SECRET_KEY` is only required when `ENVIRONMENT=production`.

Build a new image, create and up the container using:
```bash
make up
```

Using another terminal, log on container with:
```bash
make sh
```

Inside Docker container, create the DB and apply migrations running:
```bash
python3 manage.py migrate
```

## API

   - `GET /registry/` / `GET /registry/<id>` - list the chain, or a single block by index.
   - `GET /transaction/`, `POST /transaction/` - list or submit a pending transaction.
   - `GET /mine/` - mine the oldest pending transaction into a new block.
   - `GET /consensus/` - run the "longest valid chain" consensus round against known peers on demand, independent of mining.
   - `POST /node/register`, `POST /node/join` - register with / join a network of nodes.
   - `POST /node/sync_block` - receive a newly mined block announced by a peer.

## Future Improviments
   - Pass block as dict as parameter and possible delete Block class
   - Internalize nonce compute
   - Check if node exist before insert and communicate new nodes to peers

## License
Distributed under the GPL v3 License. See `LICENSE.md` for more information.
