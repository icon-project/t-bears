

# ICON SCORE development suite (tbears) TUTORIAL

## Change History

| Date       | Version  | Author | Description                                                 |
| :--------- | :---- | :----: | :--------------------------------------------------- |
| 2018.07.23 | 0.9.5 | Eunsoo Park | Improve tbears configuration files |
| 2018.07.16 | 0.9.3 | Soobok Jin | tbears cli commands updated. Document structure revised, and translated to English. |
| 2018.07.10 | 0.9.3 | Chiwon Cho | earlgrey package description added. |
| 2018.07.06 | 0.9.3 | Inwon Kim | Configuration file updated.       |
| 2018.06.12 | 0.9.2 | Chiwon Cho | Tutorial moved from doc to markdown. |
| 2018.06.11 | 0.9.1 | Chiwon Cho | Error codes added. icx_getTransactionResult description updated. |
| 2018.06.01 | 0.9.0 | Chiwon Cho | JSON-RPC API v3 ChangeLog added. |

## tbears Overview
tbears is a suite of development tools for SCORE. You can code and test your smart contract locally, and when ready, deploy SCORE onto the ICON network from command-line interface. tbears provides a project template for SCORE to help you start right away.

## Installation

This guide will explain how to install tbears on your system. 

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

Initialize SCORE development environment. Generate <project\>.py and package.json in <project\> directory. The name of the SCORE class is \<score_class\>.  Configuration files, "tbears_server_config.json" used when starting tbears and "tbears_cli_config.json" used when deploying SCORE, are also generated.

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
| tbears_cli_config.json     | Configuration file for 'deploy', 'txresult' and 'transfer' command will be created on the working directory. |
| \<project>/\_\_init\_\_.py | \_\_init\_\_.py file to make the project folder recognized as a python package. |
| \<project>/package.json    | SCORE metadata.                                              |
| \<project>/\<project>.py   | SCORE main file. ABCToken class is defined.                  |
| tests                      | Directory for SCORE unittest                                 |

#### tbears start

**Description**

Start tbears service. Whenever tbears service starts, it loads the configutaion from "tbears_server_config.json" file. If you want to use other configuration file, you can specify the file location with the '-c' option.

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
| -a, --address   | 0.0.0.0       | Address to host on              |
| -p, --port      | 9000          | Listen port                     |
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
| -t {tbears,icon},<br> --type {tbears,icon}      | tbears                       | Deploy SCORE type ("tbears" or "icon" ).                     |
| -m {install,update},<br>--mode {install,update} | install                      | Deploy mode ("install" or "update").                         |
| -f, --from                                      |                              | From address. i.e. SCORE owner address. It is ignored if '-k' option is set |
| -o, --to                                        |                              | To address. i.e. SCORE address <br>**(needed only when updating SCORE)** |
| -k, --key-store                                 |                              | Key store file for SCORE owner                               |
| -n, --nid                                       |                              | Network ID of node                                           |
| -c, --config                                    | ./tbears_cli_config.json                | deploy config path                                           |

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

Create two SCORE samples ("standard_crowd_sale", and "standard_token").

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
(work) $ transfer -f hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab 100
Got an error response
{'jsonrpc': '2.0', 'error': {'code': -32600, 'message': 'Out of balance'}, 'id': 1}

(work) $ tbears transfer -k tests/test_util/test_keystore -t real hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab 1e18
Send transfer request successfully.
transaction hash: 0xc1b92b9a08d8575f735ec2ebbf52dc831d7c2a6a2fa7e97aee4818325cad919e
```

#### tbears txresult

**Description**

Get transaction result.

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
(work) $ tbears txresult 0x2adc1c73da604c7c4247336d98bf5902eee9977ed017ffa3b2b5fd266ab3cd8d
Transaction result: {
    "jsonrpc": "2.0",
    "result": {
        "txHash": "0x2adc1c73da604c7c4247336d98bf5902eee9977ed017ffa3b2b5fd266ab3cd8d",
        "blockHeight": "0x1",
        "blockHash": "86fb191dada862c0996d883d8112baea212c4b2705676bf15f5eadb60a29de72",
        "txIndex": "0x0",
        "to": "cx0000000000000000000000000000000000000000",
        "scoreAddress": "cxeee6a1a4e8ab4d4e3d39c520ceb722217f9a9ef1",
        "stepUsed": "0x11670",
        "stepPrice": "0x0",
        "cumulativeStepUsed": "0x11670",
        "eventLogs": [],
        "logsBloom": "0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
        "status": "0x1",
        "from": "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
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

Get SCORE's api using given SCORE address

**Usage**

```bash
usage: tbears scoreapi [-h] [-u URI] [-c CONFIG] SCORE address

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
| address  |         | SCORE address to query SCORE api |
| -h, --help      |         | show this help message and exit |
| -u, --node-uri  | http://127.0.0.1:9000/api/v3 | URI of node   |
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
usage: tbears txbyhash [-h] [-u URI] [-c CONFIG] transaction hash

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
(work) $ tbears txbyhash cx0123456789abcdef0123456789abcdefabcdef12

Transaction: {
    "jsonrpc": "2.0",
    "result": {
        "method": "icx_sendTransaction",
        "params": {
            "version": "0x3",
            "from": "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "value": "0x0",
            "stepLimit": "0x300000",
            "timestamp": "0x5722d3c3a1b9e",
            "nid": "0x3",
            "nonce": "0x1",
            "to": "cx0000000000000000000000000000000000000000",
            "data": {
                "contentType": "application/tbears",
                "content": "/Users/lp1709no01/Desktop/tbears/standard_crowd_sale",
                "params": {}
            },
            "dataType": "deploy",
            "signature": "sig",
            "txHash": "95be9f0247bc3b7ed07fe07c53613c580642ef991c574c85db45dbac9e8366df"
        }
    },
    "id": 1
}

```

### tbears lastblock

**Description**

Query last block's info(Not supported in tbears server.)

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
(work) $ tbears blockbyheight 0x1

block info : {
    "jsonrpc": "2.0",
    "result": {
        "version": "0.1a",
        "prev_block_hash": "12a8cff14a8d09880a8b7db260ce003b27138a888f02c4b175a626d87b4066b0",
        "merkle_tree_root_hash": "990fb821e0499fe2c62b6e7e3259d7ddc594f3f83e85879ade9ed8379375f2ef",
        "time_stamp": 1532915456013722,
        "confirmed_transaction_list": [
            {
                "version": "0x3",
                "from": "hx3beeabe68be9c2f753d0fac917255df3ff8321c0",
                "value": "0x0",
                "stepLimit": "0x300000",
                "timestamp": "0x5722db0fb6060",
                "nid": "0x3",
                "nonce": "0x1",
                "to": "cx0000000000000000000000000000000000000000",
                "data": {
                    "contentType": "application/zip",
                    "content": "0x504b03041400000008004756fe4c65fabe8...",
                    "params": {}
                },
                "dataType": "deploy",
                "signature": "MHWDNI9P2yNTgj4EK3bt2UBcU7jRLdLighPQ/f5BPSQk3t1pgT2jxOqsCrjiSiQFL2eg/86N6hCJo4dHiX3jEwA=",
                "txHash": "0x990fb821e0499fe2c62b6e7e3259d7ddc594f3f83e85879ade9ed8379375f2ef"
            }
        ],
        "block_hash": "ce00facd0ac3832e1e6e623d8f4b9344782da881e55abb48d1494fde9e465f78",
        "height": 1,
        "peer_id": "hx86aba2210918a9b116973f3c4b27c41a54d5dafe",
        "signature": "75SpeY478raMZDVgFTXtZOa5wHZOn7nqAcWQfFgHta19IkGnRUzv/6J5hUaG+/Td55GClVrnrCn2ow1JsEV6IQA="
    },
    "id": 1
}

```

### tbears blockbyheight

**Description**

Get block's info using given block height(Not supported in tbears server.)

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
| height          |         | height of the block to be queried |
| -h, --help      |         | show this help message and exit |
| -u, --node-uri  | http://127.0.0.1:9000/api/v3 | URI of node   |
| -c, --config    | ./tbears_cli_config.json | Configuration file path. This file defines the default value for the "uri". |

**Examples**

```bash
(work) $ tbears blockbyheight 0x1

block info : {
    "jsonrpc": "2.0",
    "result": {
        "version": "0.1a",
        "prev_block_hash": "12a8cff14a8d09880a8b7db260ce003b27138a888f02c4b175a626d87b4066b0",
        "merkle_tree_root_hash": "990fb821e0499fe2c62b6e7e3259d7ddc594f3f83e85879ade9ed8379375f2ef",
        "time_stamp": 1532915456013722,
        "confirmed_transaction_list": [
            {
                "version": "0x3",
                "from": "hx3beeabe68be9c2f753d0fac917255df3ff8321c0",
                "value": "0x0",
                "stepLimit": "0x300000",
                "timestamp": "0x5722db0fb6060",
                "nid": "0x3",
                "nonce": "0x1",
                "to": "cx0000000000000000000000000000000000000000",
                "data": {
                    "contentType": "application/zip",
                    "content": "0x504b03041400000008...",
                    "params": {}
                },
                "dataType": "deploy",
                "signature": "MHWDNI9P2yNTgj4EK3bt2UBcU7jRLdLighPQ/f5BPSQk3t1pgT2jxOqsCrjiSiQFL2eg/86N6hCJo4dHiX3jEwA=",
                "txHash": "0x990fb821e0499fe2c62b6e7e3259d7ddc594f3f83e85879ade9ed8379375f2ef"
            }
        ],
        "block_hash": "ce00facd0ac3832e1e6e623d8f4b9344782da881e55abb48d1494fde9e465f78",
        "height": 1,
        "peer_id": "hx86aba2210918a9b116973f3c4b27c41a54d5dafe",
        "signature": "75SpeY478raMZDVgFTXtZOa5wHZOn7nqAcWQfFgHta19IkGnRUzv/6J5hUaG+/Td55GClVrnrCn2ow1JsEV6IQA="
    },
    "id": 1
}

```

### tbears blockbyhash

**Description**

Get block's info using given block hash(Not supported in tbears server.)

positional arguments:
  hash                  hash of the block to be queried
  
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

**Options**

| shorthand, Name | default | Description                     |
| --------------- | :------ | ------------------------------- |
| hash |         | hash of the block to be queried |
| -h, --help      |         | show this help message and exit |
| -u, --node-uri  | http://127.0.0.1:9000/api/v3 | URI of node   |
| -c, --config    | ./tbears_cli_config.json | Configuration file path. This file defines the default value for the "uri". |

**Examples**

```bash
(work) $ tbears blockbyhash ce00facd0ac3832e1e6e623d8f4b9344782da881e55abb48d1494fde9e465f78

block info : {
    "jsonrpc": "2.0",
    "result": {
        "version": "0.1a",
        "prev_block_hash": "12a8cff14a8d09880a8b7db260ce003b27138a888f02c4b175a626d87b4066b0",
        "merkle_tree_root_hash": "990fb821e0499fe2c62b6e7e3259d7ddc594f3f83e85879ade9ed8379375f2ef",
        "time_stamp": 1532915456013722,
        "confirmed_transaction_list": [
            {
                "version": "0x3",
                "from": "hx3beeabe68be9c2f753d0fac917255df3ff8321c0",
                "value": "0x0",
                "stepLimit": "0x300000",
                "timestamp": "0x5722db0fb6060",
                "nid": "0x3",
                "nonce": "0x1",
                "to": "cx0000000000000000000000000000000000000000",
                "data": {
                    "contentType": "application/zip",
                    "content": "0x504b03041400000008...",
                    "params": {}
                },
                "dataType": "deploy",
                "signature": "MHWDNI9P2yNTgj4EK3bt2UBcU7jRLdLighPQ/f5BPSQk3t1pgT2jxOqsCrjiSiQFL2eg/86N6hCJo4dHiX3jEwA=",
                "txHash": "0x990fb821e0499fe2c62b6e7e3259d7ddc594f3f83e85879ade9ed8379375f2ef"
            }
        ],
        "block_hash": "ce00facd0ac3832e1e6e623d8f4b9344782da881e55abb48d1494fde9e465f78",
        "height": 1,
        "peer_id": "hx86aba2210918a9b116973f3c4b27c41a54d5dafe",
        "signature": "75SpeY478raMZDVgFTXtZOa5wHZOn7nqAcWQfFgHta19IkGnRUzv/6J5hUaG+/Td55GClVrnrCn2ow1JsEV6IQA="
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
| hostAddress    | string    | Address to host on                                           |
| port           | int       | Port to host on                                 |
| scoreRootPath  | string    | Root directory that SCORE will be installed.                 |
| stateDbRootPath| string    | Root directory that state DB file will be created.           |
| log            | dict      | tbears log setting                                       |
| log.colorLog   | boolean   | Log display option (color or black)                         |
| log.level      | string    | log level. <br/>"debug", "info", "warning", "error"          |
| log.filePath   | string    | log file path.                                               |
| log.outputType | string    | “console”: log outputs to the console that tbears is running.<br/>“file”: log outputs to the file path.<br/>“console\|file”: log outputs to both console and file. |
| service        | didct     | tbears service setting |
| service.fee    | boolean   | not implemented                                              |
| service.audit  | boolean   | not implemented                                              |
| genesis        | dict      | genesis information of tbears node |
| genesis.nid    | string    | Network ID                                                   |
| genesis.accounts| list     | List of accounts that holds initial coins. <br>(index 0) genesis: account that holds initial coins.<br>(index 1) fee_treasury: account that collects transaction fees.<br>(index 2~): accounts. |

#### tbears_cli_config.json

When run `deploy`, `txreulst` and `transfer` commands, this file is used to configure the parameters and initial settings .

SCORE's  `on_install()` or  `on_update()`  method is called on deployment.  For example, if you deploy a new SCORE (mode: install), `on_install()` method is called to initialize the SCORE. In this config file, you can set the deploy "mode" and the parameters ("scoreParams") of `on_install()` or `on_update()`.

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
| nid         | string     | Network ID                                                   |
| keyStore    | string     | keystore file path                                |
| from        | string     | From address. It is ignored if 'keyStore' is set |
| to          | string     | To address |
| stepLimit   | string     | (optional) stepLimit value                                   |
| deploy      | dict       | options for deploy command |
| deploy.contentType | string     | SCORE type of the deployment (tbears or zip)                |
| deploy.mode        | string     | Deploy mode.<br>install: new SCORE deployment.<br>update: update the SCORE that was previously deployed. |
| deploy.scoreParams | dict       | Parameters to be passed to on_install() or on_update()       |
| deploy.from        | string     | Address of the SCORE deployer |
| deploy.to          | string     | Used when update SCORE (The address of the SCORE being updated).<br/>(in the case of "install" mode, the address should be 'cx0000~') |
| txresult    | dict       | options for txresult command |
| transfer    | dict       | options for transfer command |

Each command can have a set of options and that has a higher priority than global options

Following fields are working for each command

| Command | Field      |
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

## Notes

* tbears currently does not have loopchain engine, so some JSON-RPC APIs which are not related to SCORE development may not function.
    * Below JSON-RPC APIs are supported in tbears:
        * `icx_getBalance`, `icx_getTotalSupply`, `icx_getBalance`, `icx_call`, `icx_sendTransaction`, `icx_getTransactionResult`
* When unavoidable, tbears commands or its behavior may change for the sake of improvement.
* For the development convenience, JSON-RPC server in tbears does not verify the transaction signature.

## Reference
[tbears JSON-RPC API v3](https://repo.theloop.co.kr/icon/tbears/blob/master/docs/tbears_jsonrpc_api_v3.md)
