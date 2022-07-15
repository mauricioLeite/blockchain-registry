# Blockchain API
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Simple Blockchain implementation using as cryptographic proof the Proof-of-Work (PoW) and as consensus the longest valid chain.

## Prerequisites
   - Docker should be installed (version 20.10.17 is used on tests).
   - Docker Compose should be installed (version 1.29.2 is used on tests).

## Running

After clone the repository, create a .env file based on .env.example and use your ip address as `BLOCKCHAIN_HOST`.

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
./manage migrate
```

## Future Improviments
   - Pass block as dict as parameter and possible delete Block class
   - Internalize nonce compute
   - Implements chain rollback
   - Create nodes communication on library
   - Check if node exist before insert and communicate new nodes to peers
   - Need validation on payload strucuture

## License
Distributed under the GPL v3 License. See `LICENSE.md` for more information.