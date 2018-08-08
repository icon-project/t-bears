# ICON SCORE development suite (tbears) TUTORIAL

This tutorial is intended to give an introduction to using tbears dev suite. This guide will walk you through the basics of setting up your development environrment and the usage of tbears CLI commands. 

tbears is a suite of development tools for SCORE. You can code and test your smart contract locally, and when ready, deploy SCORE onto the ICON network from command-line interface. tbears provides a project template for SCORE to help you start right away.

## Installation

This chapter will explain how to install tbears on your system. 

### Requirements

ICON SCORE development and execution requires following environments.

* OS: MacOS, Linux
    * Windows are not supported yet.
* Python
    * Version: python 3.6+
    * IDE: Pycharm is recommended.

**Libraries**

| name        | description                                                  | github                                                       |
| ----------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| LevelDB     | ICON SCORE uses levelDB to store its states.                 | [LevelDB GitHub](https://github.com/google/leveldb)          |
| libsecp256k | ICON SCORE uses secp256k to sign and validate a digital signature. | [secp256k GitHub](https://github.com/bitcoin-core/secp256k1) |

### Setup on MacOS

```bash
#install levelDB
$ brew install leveldb

# Create a working directory
$ mkdir work
$ cd work

# setup the python virtualenv development environment
$ virtualenv -p python3 .
$ source bin/activate

# Install the ICON SCORE dev tools
(work) $ pip install earlgrey-x.x.x-py3-none-any.whl
(work) $ pip install iconcommons-x.x.x-py3-none-any.whl
(work) $ pip install iconservice-x.x.x-py3-none-any.whl
(work) $ pip install tbears-x.x.x-py3-none-any.whl
```

### Setup on Linux

```bash
# Install levelDB
$ sudo apt-get install libleveldb1 libleveldb-dev
# Install libSecp256k
$ sudo apt-get install libsecp256k1-dev

# Create a working directory
$ mkdir work
$ cd work

# Setup the python virtualenv development environment
$ virtualenv -p python3 .
$ source bin/activate

# Install the ICON SCORE dev tools
(work) $ pip install earlgrey-x.x.x-py3-none-any.whl
(work) $ pip install iconcommons-x.x.x-py3-none-any.whl
(work) $ pip install iconservice-x.x.x-py3-none-any.whl
(work) $ pip install tbears-x.x.x-py3-none-any.whl
```

## How to use tbears

### Command-line Interfaces(CLIs)

#### Overview

tbears has 16 commands, `init`, `start`, `stop`, `deploy`, `clear`, `samples`, `transfer`, `txresult`, `balance`,
`totalsupply`, `scoreapi`, `txbyhash`, `lastblock`, `blockbyheight`, `blockbyhash` and `keystore`.

**Usage**

```bash
usage: tbears [-h] [-d] command ...

tbears v0.9.5 arguments

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           Debug mode

Available commands:
  If you want to see help message of commands, use "tbears command -h"

  command
    start           Start tbears serivce
    stop            Stop tbears service
    deploy          Deploy the SCORE
    clear           Clear all SCORE deployed on tbears service
    init            Initialize tbears project
    samples         Create two SCORE samples (standard_crowd_sale, standard_token)
    transfer        transfer ICX coin
    balance         Get balance of given address
    totalsupply     Get total supply of ICX
    scoreapi        Get SCORE's api using given SCORE address
    txresult        Get transaction result by transaction hash
    txbyhash        Get transaction by transaction hash
    lastblock       Get last block's info
    blockbyheight   Get block info by block hash
    blockbyhash     Get block info by block height
    keystore   Create keystore file in passed path
```

**Options**

| shorthand, Name | default | Description                     |
| --------------- | :------ | ------------------------------- |
| -h, --help      |         | show this help message and exit |
| -d, --debug     |         | Debug mode                      |

#### tbears init

**Description**

Initialize SCORE development environment. Generate <project\>.py and package.json in <project\> directory. The name of the SCORE class is \<score_class\>.  Default configuration files, "tbears_server_config.json" used when starting tbears and "tbears_cli_config.json" used when deploying SCORE, are also generated.

**Usage**

```bash
usage: tbears init [-h] project score_class
Initialize SCORE development environment. Generate <project>.py and
package.json in <project> directory. The name of the SCORE class is
<score_class>.

positional arguments:
  project      Project name
  score_class  SCORE class name

optional arguments:
  -h, --help   show this help message and exit
```

**Options**

| shorthand, Name | default | Description                     |
| --------------- | :------ | ------------------------------- |
| project         |         | Project name                    |
| score_class     |         | SCORE class name                |
| -h, --help      |         | show this help message and exit |

**Examples**

```bash
(work) $ tbears init abc ABCToken
(work) $ ls abc
abc.py  __init__.py package.json tests
```

**File description**

| **Item**                   | **Description**                                              |
| :------------------------- | :----------------------------------------------------------- |
| \<project>                 | SCORE project name. Project directory is create with the same name. |
| tbears_server_config.json  | tbears default configuration file will be created on the working directory. |
| tbears_cli_config.json     | Configuration file for CLI commands will be created on the working directory. |
| \<project>/\_\_init\_\_.py | \_\_init\_\_.py file to make the project folder recognized as a python package. |
| \<project>/package.json    | SCORE metadata.                                              |
| \<project>/\<project>.py   | SCORE main file. ABCToken class is defined.                  |
| tests                      | Directory for SCORE unittest                                 |

#### tbears start

**Description**

Start tbears service. Whenever tbears service starts, it loads the configutaion from "tbears_server_config.json" file. If you want to use other configuration file, you can specify the file location with the '-c' option.

**Usage**

```bash
usage: tbears start [-h] [-a ADDRESS] [-p PORT] [-c CONFIG]

Start tbears service

optional arguments:
  -h, --help                       show this help message and exit
  -a ADDRESS, --address ADDRESS    Address to host on (default: 0.0.0.0)
  -p PORT, --port PORT             Listen port (default: 9000)
  -c CONFIG, --config CONFIG       tbears configuration file path(default:./tbears_server_config.json)
```

**Options**

| shorthand, Name | default       | Description                     |
| --------------- | :------------ | ------------------------------- |
| -h, --help      |               | show this help message and exit |
| -a, --address   | 0.0.0.0       | IP address that the tbears service will listen on. |
| -p, --port      | 9000          | Port number that the tbears service will listen on. |
| -c, --config    | ./tbears_server_config.json | tbears configuration file path  |

#### tbears stop

**Description**

Stop all running SCOREs and tbears service.

**Usage**

```bash
usage: tbears stop [-h]

Stop all running SCORE and tbears service

optional arguments:
  -h, --help  show this help message and exit
```

**Options**

| shorthand, Name | default | Description                     |
| --------------- | :------ | ------------------------------- |
| -h, --help      |         | show this help message and exit |

#### tbears deploy

**Description**

Deploy the SCORE. You can deploy it on local or icon service.

"tbears_cli_config.json" file contains deploymenet configuration properties. (See below 'Configuration Files' chapter). If you want to use other configuration file, you can specify the file location with the '-c' option.

**Usage**

```bash
usage: tbears deploy [-h] [-u URI] [-t {tbears,icon}] [-m {install,update}]
                     [-f FROM] [-o TO] [-k KEYSTORE] [-c CONFIG]
                     project

Deploy the SCORE in project

positional arguments:
  project               Project name

optional arguments:
  -h, --help                                   show this help message and exit
  -u URI, --node-uri URI                       URI of node
                                               (default: http://127.0.0.1:9000/api/v3)
  -t {tbears,zip}, --type {tbears,zip}         Deploy SCORE type
                                               (default: tbears)
  -m {install,update}, --mode {install,update} Deploy mode (default: install)
  -f FROM, --from FROM                         From address. i.e. SCORE owner address
  -o TO, --to TO                               To address. i.e. SCORE address
  -k KEYSTORE, --key-store KEYSTORE            Key store file for SCORE owner
  -n NID, --nid NID                            Network ID of node
  -c CONFIG, --config CONFIG                   deploy config path (default: ./tbears_cli_config.json)
```

**Options**

| shorthand, Name                                 | default                      | Description                                                  |
| ----------------------------------------------- | :--------------------------- | ------------------------------------------------------------ |
| project                                         |                              | Project directory which contains the SCORE package.          |
| -h, --help                                      |                              | show this help message and exit                              |
| -u, --node-uri                                  | http://127.0.0.1:9000/api/v3 | URI of node                                                  |
| -t {tbears,icon},<br> --type {tbears,zip}       | tbears                       | Deploy SCORE type ("tbears" or "zip" ).<br>Use "tbears" for local deploy.  When deploy to remote network, you must use "zip". |
| -m {install,update},<br>--mode {install,update} | install                      | Deploy mode ("install" or "update").                         |
| -f, --from                                      |                              | From address. i.e. SCORE owner address. It is ignored if '-k' option is set |
| -o, --to                                        |                              | To address. i.e. SCORE address <br>This parameter is required when updating SCORE. |
| -k, --key-store                                 |                              | Key store file for SCORE owner                               |
| -n, --nid                                       |                              | Network ID of node. <br>Each network has unique ID. If the Nerwork ID does not match, node will reject the SCORE. Network ID will be announced when a network opens to public.<br>0x3 is reserved for tbears service. However, tbears service does not verify the Network id. |
| -c, --config                                    | ./tbears_cli_config.json     | Configuration file path                                      |

**Examples**

```bash
(Work)$ tbears deploy -t tbears abc

(work)$ tbears deploy abc -c ./tbears_cli_config.json

#when you deploy SCORE to icon, input keystore password
(Work)$ tbears deploy -t icon -f hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa -k keystore abc
input your key store password:

Send deploy request successfully.
transaction hash: 0x9c294b9608d9575f735ec2e2bf52dc891d7cca6a2fa7e97aee4818325c8a9d41

#update abc SCORE
#append prefix 'cx' in front of SCORE address
(Work)$ tbears deploy abc -m update -o cx6bd390bd855f086e3e9d525b46bfe24511431532
Send deploy request successfully.
transaction hash: 0xad292b9608d9575f735ec2ebbf52dc891d7cca6a2fa7e97aee4818325c80934d
```

#### tbears clear

**Description**

Clear all SCOREs deployed on local tbears service.

**Usage**

```bash
usage: tbears clear [-h]

Clear all SCOREs deployed on local tbears service

optional arguments:
  -h, --help  show this help message and exit
```

**Options**

| shorthand, Name | default | Description                     |
| --------------- | :------ | ------------------------------- |
| -h, --help      |         | show this help message and exit |

#### tbears samples

**Description**

Create two SCORE samples ("standard_crowd_sale" and "standard_token").

**usage**

```bash
usage: tbears samples [-h]

Create two SCORE samples (standard_crowd_sale, standard_token)

optional arguments:
  -h, --help  show this help message and exit
```

**Options**

| shorthand, Name | default | Description                     |
| --------------- | :------ | ------------------------------- |
| -h, --help      |         | show this help message and exit |

**Examples**

```bash
(work) $ tbears samples

(work) $ ls standard*
standard_crowd_sale:
__init__.py  package.json  standard_crowd_sale.py

standard_token:
__init__.py  package.json  standard_token.py
```

#### tbears transfer

**Description**

Transfer designated amount of ICX coins.

**Usage**

```bash
usage: tbears transfer [-h] [-f FROM] [-t {dummy,real}] [-k KEYSTORE] [-u URI]
                       [-c CONFIG]
                       to value

Transfer ICX coin.

positional arguments:
  to                    Recipient
  value                 Amount of ICX coin to transfer in loop(1 icx = 1e18
                        loop)

optional arguments:
  -h, --help            show this help message and exit
  -f FROM, --from FROM  From address. Must use with dummy type.
  -k KEYSTORE, --key-store KEYSTORE
                        Sender's key store file
  -u URI, --node-uri URI
                        URI of node (default: http://127.0.0.1:9000/api/v3)
  -c CONFIG, --config CONFIG
                        deploy config path (default: ./tbears_cli_config.json)
```

**Options**

| shorthand, Name | default | Description                     |
| --------------- | :------ | ------------------------------- |
| to              |         | Recipient address.          |
| value           |         | Amount of ICX coin in loop to transfer to "to" address. (1 icx = 1e18 loop) |
| -h, --help      |         | show this help message and exit |
| -f, --from      |         | From address. It is ignored if '-k' option is set|
| -k, --key-store |         | Keystore file path. Used to generate "from" address and transaction signature. |
| -u, --node-uri  | http://127.0.0.1:9000/api/v3 | URI of node                                                  |
| -n, --nid       | 0x3     | Network ID |
| -c, --config    | ./tbears_cli_config.json | Configuration file path. This file defines the default values for the properties "keyStore", "uri" and "from". |

**Examples**

```bash
(work) $ transfer -f hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa hxbbaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab 100
Got an error response
{'jsonrpc': '2.0', 'error': {'code': -32600, 'message': 'Out of balance'}, 'id': 1}

(work) $ tbears transfer -k test_keystore hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab 1e18
Send transfer request successfully.
transaction hash: 0xc1b92b9a08d8575f735ec2ebbf52dc831d7c2a6a2fa7e97aee4818325cad919e
```

#### tbears txresult

**Description**

Get transaction result by transaction hash.

**Usage**

```bash
usage: tbears txresult [-h] [-u URI] [-c CONFIG] hash

Get transaction result by transaction hash

positional arguments:
  hash                  Transaction hash of the transaction to be queried.

optional arguments:
  -h, --help            show this help message and exit
  -u URI, --node-uri URI
                        URI of node (default: http://127.0.0.1:9000/api/v3)
  -c CONFIG, --config CONFIG
                        config path. Use "uri" value (default: ./tbears_cli_config.json)
```

**Options**

| shorthand, Name | default | Description                     |
| --------------- | :------ | ------------------------------- |
| hash  |         | Hash of the transaction to be queried |
| -h, --help      |         | show this help message and exit |
| -u, --node-uri  | http://127.0.0.1:9000/api/v3 | URI of node   |
| -c, --config    | ./tbears_cli_config.json | Configuration file path. This file defines the default value for the "uri". |

**Examples**

```bash
(work) $ tbears txresult 0x227fb3e6fdc89de8d24e019b1ddc88538633c4202102297da204444d393249c2
Transaction result: {
    "jsonrpc": "2.0",
    "result": {
        "txHash": "0x227fb3e6fdc89de8d24e019b1ddc88538633c4202102297da204444d393249c2",
        "blockHeight": "0x2",
        "blockHash": "28e6e4710c56e053920b95df0058317a4ac641b16d17d64db7f958e8a5650391",
        "txIndex": "0x0",
        "to": "cx0000000000000000000000000000000000000000",
        "scoreAddress": "cx6bd390bd855f086e3e9d525b46bfe24511431532",
        "stepUsed": "0xe2a4",
        "stepPrice": "0x0",
        "cumulativeStepUsed": "0xe2a4",
        "eventLogs": [],
        "logsBloom": "0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
        "status": "0x1"
    },
    "id": 1
}
```

### tbears balance

**Description**

Get balance of given address.

**Usage**

```bash
usage: tbears balance [-h] [-u URI] [-c CONFIG] address

Get balance of given address

positional arguments:
  address                  Address to query the icx balance.

optional arguments:
  -h, --help            show this help message and exit
  -u URI, --node-uri URI
                        URI of node (default: http://127.0.0.1:9000/api/v3)
  -c CONFIG, --config CONFIG
                        config path. Use "uri" value (default: ./tbears_cli_config.json)
```

**Options**

| shorthand, Name | default | Description                     |
| --------------- | :------ | ------------------------------- |
| address  |    | Address to query the icx balance |
| -h, --help      |         | show this help message and exit |
| -u, --node-uri  | http://127.0.0.1:9000/api/v3 | URI of node   |
| -c, --config    | ./tbears_cli_config.json | Configuration file path. This file defines the default value for the "uri". |

**Examples**

```bash
(work) $ tbears balance hx0123456789abcdef0123456789abcdefabcdef12

balance : 0x2961fff8ca4a62327800000
```

### tbears totalsupply

**Description**

Query total supply of ICX.

**Usage**

```bash
usage: tbears totalsupply [-h] [-u URI] [-c CONFIG]

Get total supply of ICX

optional arguments:
  -h, --help            show this help message and exit
  -u URI, --node-uri URI
                        URI of node (default: http://127.0.0.1:9000/api/v3)
  -c CONFIG, --config CONFIG
                        config path. Use "uri" value (default: ./tbears_cli_config.json)
```

**Options**

| shorthand, Name | default | Description                     |
| --------------- | :------ | ------------------------------- |
| -h, --help      |         | show this help message and exit |
| -u, --node-uri  | http://127.0.0.1:9000/api/v3 | URI of node   |
| -c, --config    | ./tbears_cli_config.json | Configuration file path. This file defines the default value for the "uri". |

**Examples**

```bash
(work) $ tbears totalsupply

Total supply  of Icx: 0x2961fff8ca4a62327800000
```

### tbears scoreapi

**Description**

Get SCORE's APIs using given SCORE address.

**Usage**

```bash
usage: tbears scoreapi [-h] [-u URI] [-c CONFIG] address

Get SCORE's api using given SCOREaddress

positional arguments:
  address                  SCORE address to query SCORE api

optional arguments:
  -h, --help            show this help message and exit
  -u URI, --node-uri URI
                        URI of node (default: http://127.0.0.1:9000/api/v3)
  -c CONFIG, --config CONFIG
                        config path. Use "uri" value (default: ./tbears_cli_config.json)
```

**Options**

| shorthand, Name | default | Description                     |
| --------------- | :------ | ------------------------------- |
| address  |         | SCORE address to query APIs |
| -h, --help      |         | show this help message and exit |
| -u, --node-uri  | http://127.0.0.1:9000/api/v3 | URI of node.  |
| -c, --config    | ./tbears_cli_config.json | Configuration file path. This file defines the default value for the "uri". |

**Examples**

```bash
(work) $ tbears scoreapi cx0123456789abcdef0123456789abcdefabcdef12

scoreAPI: [
    {
        "type": "fallback",
        "name": "fallback",
        "inputs": []
    },
    {
        "type": "function",
        "name": "hello",
        "inputs": [],
        "outputs": [
            {
                "type": "str"
            }
        ],
        "readonly": "0x1"
    }
]

```

### tbears txbyhash

**Description**

Get transaction by transaction hash

**Usage**

```bash
usage: tbears txbyhash [-h] [-u URI] [-c CONFIG] hash

Get transaction by transaction hash

positional arguments:
  hash                  Hash of the transaction to be queried

optional arguments:
  -h, --help            show this help message and exit
  -u URI, --node-uri URI
                        URI of node (default: http://127.0.0.1:9000/api/v3)
  -c CONFIG, --config CONFIG
                        config path. Use "uri" value (default: ./tbears_cli_config.json)
```

**Options**

| shorthand, Name | default | Description                     |
| --------------- | :------ | ------------------------------- |
| hash  |         | Hash of the transaction to be queried |
| -h, --help      |         | show this help message and exit |
| -u, --node-uri  | http://127.0.0.1:9000/api/v3 | URI of node   |
| -c, --config    | ./tbears_cli_config.json | Configuration file path. This file defines the default value for the "uri". |

**Examples**

```bash
(work) $ tbears txbyhash 0x95be9f0247bc3b7ed07fe07c53613c580642ef991c574c85db45dbac9e8366df

Transaction: {
    "jsonrpc": "2.0",
    "result": {
        "version": "0x3",
        "from": "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "value": "0x0",
        "stepLimit": "0x300000",
        "timestamp": "0x572e8fd95db26",
        "nid": "0x3",
        "nonce": "0x1",
        "to": "cx0000000000000000000000000000000000000000",
        "data": {
            "contentType": "application/tbears",
            "content": "/Users/lp1709no01/Desktop/abc/abc",
            "params": {}
        },
        "dataType": "deploy",
        "signature": "sig",
        "txIndex": "0x0",
        "blockHeight": "0x2",
        "blockHash": "0x28e6e4710c56e053920b95df0058317a4ac641b16d17d64db7f958e8a5650391"
    },
    "id": 1
}

```

### tbears lastblock

**Description**

Query last block info. When running on tbears service, "merkle_tree_root_hash" and "signature" will be empty. 

**Usage**

```bash
usage: tbears lastblock [-h] [-u URI] [-c CONFIG]

Get last block's info

optional arguments:
  -h, --help            show this help message and exit
  -u URI, --node-uri URI
                        URI of node (default: http://127.0.0.1:9000/api/v3)
  -c CONFIG, --config CONFIG
                        config path. Use "uri" value (default: ./tbears_cli_config.json)
```

**Options**

| shorthand, Name | default | Description                     |
| --------------- | :------ | ------------------------------- |
| -h, --help      |         | show this help message and exit |
| -u, --node-uri  | http://127.0.0.1:9000/api/v3 | URI of node   |
| -c, --config    | ./tbears_cli_config.json | Configuration file path. This file defines the default value for the "uri". |

**Examples**

```bash
(work) $ tbears lastblock 

block info : {
    "jsonrpc": "2.0",
    "result": {
        "version": "tbears",
        "prev_block_hash": "815c0fd7a0dd4594bb19ee39030c1bd91c200878f1f456fe8dd7ff4e0a19b839",
        "merkle_tree_root_hash": "tbears_does_not_support_merkel_tree",
        "time_stamp": 1533719896011654,
        "confirmed_transaction_list": [
            {
                "version": "0x3",
                "from": "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "value": "0x0",
                "stepLimit": "0x300000",
                "timestamp": "0x572e8fd95db26",
                "nid": "0x3",
                "nonce": "0x1",
                "to": "cx0000000000000000000000000000000000000000",
                "data": {
                    "contentType": "application/tbears",
                    "content": "/Users/lp1709no01/Desktop/abc/abc",
                    "params": {}
                },
                "dataType": "deploy",
                "signature": "sig"
            }
        ],
        "block_hash": "28e6e4710c56e053920b95df0058317a4ac641b16d17d64db7f958e8a5650391",
        "height": 2,
        "peer_id": "fb5f43dc-9aeb-11e8-a31b-acde48001122",
        "signature": "tbears_does_not_support_signature"
    },
    "id": 1
}

```

### tbears blockbyheight

**Description**

Get block info using given block height.

**Usage**

```bash
usage: tbears blockbyheight [-h] [-u URI] [-c CONFIG] height

Get block's info using given block height

positional arguments:
  height                  height of the block to be queried
  
optional arguments:
  -h, --help            show this help message and exit
  -u URI, --node-uri URI
                        URI of node (default: http://127.0.0.1:9000/api/v3)
  -c CONFIG, --config CONFIG
                        config path. Use "uri" value (default: ./tbears_cli_config.json)
```

**Options**

| shorthand, Name | default | Description                     |
| --------------- | :------ | ------------------------------- |
| height          |         | Height of the block to be queried |
| -h, --help      |         | show this help message and exit |
| -u, --node-uri  | http://127.0.0.1:9000/api/v3 | URI of node   |
| -c, --config    | ./tbears_cli_config.json | Configuration file path. This file defines the default value for the "uri". |

**Examples**

```bash
(work) $ tbears blockbyheight 0x1

block info : {
    "jsonrpc": "2.0",
    "result": {
        "version": "tbears",
        "prev_block_hash": "859083707985809a8b52982b9d8d86bfe48c0020a478b3a99d7eeb3c74c38e7c",
        "merkle_tree_root_hash": "tbears_does_not_support_merkel_tree",
        "time_stamp": 1533719753948440,
        "confirmed_transaction_list": [
            {
                "version": "0x3",
                "from": "hxef73db5d0ad02eb1fadb37d0041be96bfa56d4e6",
                "value": "0x8ac7230489e80000",
                "stepLimit": "0x2000",
                "timestamp": "0x572e8f51e4481",
                "nid": "0x3",
                "nonce": "0x1",
                "to": "hxbbaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab",
                "signature": "f2B3r27u7peL3I9uBnKA8yn82odqlMECU+UBkRiZTJIwWFo57AmlUjKhoK8OZBBRdaWWmLF+JTZNs70yF8+zIwA="
            }
        ],
        "block_hash": "815c0fd7a0dd4594bb19ee39030c1bd91c200878f1f456fe8dd7ff4e0a19b839",
        "height": 1,
        "peer_id": "a6b22354-9aeb-11e8-a0ae-acde48001122",
        "signature": "tbears_does_not_support_signature"
    },
    "id": 1
}

```

### tbears blockbyhash

**Description**

Get block info using given block hash.

**Options**

| shorthand, Name | default                      | Description                                                  |
| --------------- | :--------------------------- | ------------------------------------------------------------ |
| hash            |                              | Hash of the block to be queried                              |
| -h, --help      |                              | show this help message and exit                              |
| -u, --node-uri  | http://127.0.0.1:9000/api/v3 | URI of node                                                  |
| -c, --config    | ./tbears_cli_config.json     | Configuration file path. This file defines the default value for the "uri". |

**Usage**

```bash
usage: tbears blockbyhash [-h] [-u URI] [-c CONFIG] hash

Get block's info using given block hash

positional arguments:
  hash                  hash of the block to be queried
  
optional arguments:
  -h, --help            show this help message and exit
  -u URI, --node-uri URI
                        URI of node (default: http://127.0.0.1:9000/api/v3)
  -c CONFIG, --config CONFIG
                        config path. Use "uri" value (default: ./tbears_cli_config.json)
```

**Examples**

```bash
(work) $ tbears blockbyhash 0xce00facd0ac3832e1e6e623d8f4b9344782da881e55abb48d1494fde9e465f78

block info : {
    "jsonrpc": "2.0",
    "result": {
        "version": "tbears",
        "prev_block_hash": "859083707985809a8b52982b9d8d86bfe48c0020a478b3a99d7eeb3c74c38e7c",
        "merkle_tree_root_hash": "tbears_does_not_support_merkel_tree",
        "time_stamp": 1533719753948440,
        "confirmed_transaction_list": [
            {
                "version": "0x3",
                "from": "hxef73db5d0ad02eb1fadb37d0041be96bfa56d4e6",
                "value": "0x8ac7230489e80000",
                "stepLimit": "0x2000",
                "timestamp": "0x572e8f51e4481",
                "nid": "0x3",
                "nonce": "0x1",
                "to": "hxbbaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab",
                "signature": "f2B3r27u7peL3I9uBnKA8yn82odqlMECU+UBkRiZTJIwWFo57AmlUjKhoK8OZBBRdaWWmLF+JTZNs70yF8+zIwA="
            }
        ],
        "block_hash": "815c0fd7a0dd4594bb19ee39030c1bd91c200878f1f456fe8dd7ff4e0a19b839",
        "height": 1,
        "peer_id": "a6b22354-9aeb-11e8-a0ae-acde48001122",
        "signature": "tbears_does_not_support_signature"
    },
    "id": 1
}

```

### tbears keystore

**Description**

Create keystore file in passed path

positional arguments:
  path                  path of keystore file

**Usage**

```bash
usage: tbears keystore [-h] [-u URI] [-c CONFIG] path

Create keystore file in passed path

positional arguments:
  path                  Create keystore file in passed path
```

**Options**

| shorthand, Name | default | Description                     |
| --------------- | :------ | ------------------------------- |
| path | | Create keystore file in passed path |

**Examples**

```bash
(work) $ tbears keystore keystorepath

input your key store password: (You have to initialize your keystore password)

Made keystore file successfully

```

### Configuration Files

#### tbears_server_config.json

When starting tbears (`tbears start`), "tbears_server_config.json" is used to configure the parameters and initial settings.

```json
{
    "hostAddress": "0.0.0.0",
    "port": 9000,
    "scoreRootPath": "./.score",
    "stateDbRootPath": "./.statedb",
    "log": {
        "colorLog": true,
        "level": "info",
        "filePath": "./tbears.log",
        "outputType": "console|file"
    },
    "service": {
        "fee": false,
        "audit": false
    },
    "genesis": {
        "nid": "0x03",
        "accounts": [
            {
                "name": "genesis",
                "address": "hx0000000000000000000000000000000000000000",
                "balance": "0x2961fff8ca4a62327800000"
            },
            {
                "name": "fee_treasury",
                "address": "hx1000000000000000000000000000000000000000",
                "balance": "0x0"
            }
        ]
    }
}
```

| Field          | Data type | Description                                                  |
| :------------- | :-------- | :----------------------------------------------------------- |
| hostAddress    | string    | IP address that tbears service will listen on. |
| port           | int       | Port number that tbears service will listen on. |
| scoreRootPath  | string    | Root directory that SCORE will be installed.                 |
| stateDbRootPath| string    | Root directory that state DB file will be created.           |
| log            | dict      | tbears log setting                                       |
| log.colorLog   | boolean   | Log display option (color or black)                         |
| log.level      | string    | log level. <br/>"debug", "info", "warning", "error"          |
| log.filePath   | string    | Log file path.                                              |
| log.outputType | string    | “console”: log outputs to the console that tbears is running.<br/>“file”: log outputs to the file path.<br/>“console\|file”: log outputs to both console and file. |
| service        | didct     | tbears service setting |
| service.fee    | boolean   | true \| false. Default is false.        |
| service.audit  | boolean   | true \| false. Default is false.          |
| genesis        | dict      | Genesis information of tbears node. |
| genesis.nid    | string    | Network ID.                                                 |
| genesis.accounts| list     | List of accounts that holds initial coins. <br>(index 0) genesis: account that holds initial coins.<br>(index 1) fee_treasury: account that collects transaction fees.<br>(index 2~): test accounts that you can add. |

#### tbears_cli_config.json

For every tbears CLI commands except `start`, `stop`, `samples`, `clear` and `init`, this file is used to configure the default parameters and initial settings.  

In this cofiguration file, you can define default options values for some CLI commnds. For example, SCORE's  `on_install()` or  `on_update()`  method is called on deployment. In this config file, you can set the deploy "mode" and the parameters ("scoreParams") of `on_install()` or `on_update()` as shown in the following example.

```json
{
    "uri": "http://127.0.0.1:9000/api/v3",
    "nid": "0x3",
    "keyStore": null,
    "from": "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "to": "cx0000000000000000000000000000000000000000",
    "stepLimit": "0x2000",
    "deploy": {
        "contentType": "tbears",
        "mode": "install",
        "scoreParams": {}
    },
    "txresult": {},
    "transfer": {}
}
```

| Field       | Data  type | Description                                                  |
| ----------- | :--------- | :----------------------------------------------------------- |
| uri         | string     | uri to send the request.                              |
| nid         | string     | Network ID. 0x03 is reserved for tbears.  |
| keyStore    | string     | Keystore file path.                              |
| from        | string     | From address. It is ignored if 'keyStore' is set. |
| to          | string     | To address. |
| stepLimit   | string     | (optional) stepLimit value. Default is 0x300000. |
| deploy      | dict       | Options for deploy command. |
| deploy.contentType | string     | SCORE type for the deployment. ("tbears" or "zip")        |
| deploy.mode        | string     | Deploy mode.<br>install: new SCORE deployment.<br>update: update the SCORE that was previously deployed. |
| deploy.scoreParams | dict       | Parameters to be passed to on_install() or on_update()       |
| deploy.from        | string     | Address of the SCORE deployer<br>Optional. This value will override "from" value. If not given, "from" value will be used. |
| deploy.to          | string     | Used when update SCORE (The address of the SCORE being updated).<br/>In the case of "install" mode, the address should be 'cx0000~'.<br>Optional. This value will override "to" value. If not given, "to" value will be used. |
| txresult    | dict       | Options for txresult command.<br>You can define command options in a dict. |
| transfer    | dict       | Options for transfer command.<br>You can define command options in a dict. |

Following CLI commands and options can be defined in the configuration file.  

| Command | Options |
| ------- | :--------- |
| deploy  | uri, nid, keyStore, from, to, mode, contentType, scoreParams, stepLimit |
| txresult| uri |
| transfer| uri, nid, keyStore, from, to, stepLimit |

## Utilities

Utilities for SCORE development.

### Logger

Logger is a package writing outputs to log file or console.

#### Method

```python
@staticmethod
def debug(msg: str, tag: str)
```

#### Usage

```python
from iconservice.logger import Logger

TAG = 'ABCToken'

Logger.debug('debug log', TAG)
Logger.info('info log', TAG)
Logger.warning('warning log', TAG)
Logger.error('error log', TAG)
```




