# This repository archived. Refer to ICON 2.0 aka [goloop](https://github.com/icon-project/goloop).

----

# ICON SCORE Development Suite (T-Bears) Tutorial

This tutorial is intended to give an introduction to using T-Bears. This guide will walk you through the basics of setting up your development environment and the usage of T-Bears CLI commands.

T-Bears is a suite of development tools for SCORE. T-Bears provides a project template for SCORE to help you start right away. You can code and test your smart contract locally in an emulated environment, and when ready, deploy SCORE onto the ICON network from command-line interface.

## Components
![Components](https://github.com/icon-project/t-bears/raw/master/images/components.png)

### ICON RPC Server
A module that handles ICON JSON-RPC API request and sends response back to the client.

### ICON Service
A module that manages the lifecycle of SCORE and its execution. SCORE's state transition is stored in a database.

### T-Bears CLI
T-Bears Command Line Interface. Supports following functions:
 * Manage T-Bears service
 * Deploy SCORE
 * Send transaction
 * Send query request

For the details, see below '[Command-line Interfaces (CLIs)](#command-line-interfaces-clis)' chapter.

### T-Bears Block Manager
Loopchain emulator for T-Bears Service. It does not have full 'consensus' and 'peer management' functions. This module handles transaction and emulates block generation.

### Message queue
Message queue is used for inter-component communication.


## Quick start
You can run T-Bears on your machine by using Docker.

The below command will download T-Bears Docker image and run T-Bears Docker container.

```bash
docker run -it -p 9000:9000 iconloop/tbears:mainnet
```
Please check the following links for more information. [T-Bears Docker](https://github.com/icon-project/t-bears/tree/master/Docker)

## Building from source
 First, clone this project. Then go to the project directory, create a virtualenv environment, and run build script. You can then install T-Bears with the .whl file.
```bash
$ virtualenv -p python3 venv  # Create a virtual environment.
$ source venv/bin/activate    # Enter the virtual environment.
(venv)$ ./build.sh            # run build script
(venv)$ ls dist/              # check result wheel file
tbears-x.y.z-py3-none-any.whl
```

## Installation

This chapter will explain how to install T-Bears on your system.

### Requirements

ICON SCORE development and execution requires following environments :

* OS: MacOS or Linux
  * Windows is not supported.
  
* Python
  * Make a virtualenv for Python 3.7
  * Check your Python version
    ```bash
    $ python3 -V
    ```
  * IDE: Pycharm is recommended.

**Softwares**

* RabbitMQ: 3.7 and above. [homepage](https://www.rabbitmq.com/)
* Reward calculator. [homepage](https://github.com/icon-project/rewardcalculator)

**Libraries**

| name        | description                                                  | github                                                       |
| ----------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| LevelDB     | ICON SCORE uses levelDB to store its states.                 | [LevelDB GitHub](https://github.com/google/leveldb)          |

### Setup on MacOS

```bash
# install develop tools
$ brew install leveldb
$ brew install autoconf automake libtool pkg-config

# install RabbitMQ and start service
$ brew install rabbitmq
$ brew services start rabbitmq

# Create a working directory
$ mkdir work
$ cd work

# install Reward calculator
$ git clone https://github.com/icon-project/rewardcalculator.git
$ cd rewardcalculator
$ make
$ make install

# setup the python virtualenv development environment
$ pip3 install virtualenv
$ virtualenv -p python3 .
$ source bin/activate

# Install the ICON SCORE dev tools
(work) $ pip install tbears
```

### Setup on Linux

```bash
# Install levelDB
$ sudo apt-get install libleveldb-dev

# install RabbitMQ and start service
$ sudo apt-get install rabbitmq-server
$ sudo service rabbitmq-server start

# Create a working directory
$ mkdir work
$ cd work

# install Reward calculator
$ git clone https://github.com/icon-project/rewardcalculator.git
$ cd rewardcalculator
$ make
$ make install

# Setup the python virtualenv development environment
$ virtualenv -p python3 .
$ source bin/activate

# Install the ICON SCORE dev tools
(work) $ pip install tbears
```

## How to use T-Bears

### Command-line Interfaces (CLIs)

#### Overview

T-Bears provides over 20 commands. Here is the available commands list.

**Usage**

```bash
usage: tbears [-h] [-v] command ...

tbears v1.2.1 arguments

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  Verbose mode

Available commands:
  If you want to see help message of commands, use "tbears command -h"

  command
    start        Start tbears service
    stop         Stop tbears service
    sync_mainnet
                 Synchronize revision and governance SCORE with the mainnet
    deploy       Deploy the SCORE
    clear        Clear all SCOREs deployed on tbears service
    test         Run the unittest in the SCORE
    init         Initialize tbears project
    samples      This command has been deprecated since v1.1.0
    genconf      Generate tbears config files. (tbears_server_config.json,
                 tbears_cli_config.json and keystore_test1)
    console      Get into tbears interactive mode by embedding IPython
    txresult     Get transaction result by transaction hash
    transfer     Transfer ICX coin.
    keystore     Create a keystore file in the specified path
    keyinfo      Show a keystore file information the specified path
    balance      Get balance of given address in loop unit
    totalsupply  Query total supply of ICX in loop unit
    scoreapi     Get score's api using given score address
    txbyhash     Get transaction by transaction hash
    lastblock    Get last block's info
    blockbyhash  Get block info using given block hash
    blockbyheight
                 Get block info using given block height
    sendtx       Request icx_sendTransaction with the specified json file and
                 keystore file. If keystore file is not given, tbears sends
                 request as it is in the json file.
    call         Request icx_call with the specified json file.
```

**Options**

| shorthand, Name | default | Description                     |
| :-------------- | :------ | :------------------------------ |
| -h, --help      |         | Show this help message and exit |
| -v, --verbose   |         | Verbose mode. Print debugging messages about its progress. |



### T-Bears server commands

Commands that manage the T-Bears server. There are three commands `tbears start`, `tbears stop`, `tbears clear` and `tbears sync_mainnet`.

#### tbears start

**Description**

Start T-Bears service. Whenever T-Bears service starts, it loads the configuration from `tbears_server_config.json` file. If you want to use other configuration file, you can specify the file location with the `-c` option.

**Usage**

```bash
usage: tbears start [-h] [-a HOSTADDRESS] [-p PORT] [-c CONFIG]

Start tbears service

optional arguments:
  -h, --help            show this help message and exit
  -a HOSTADDRESS, --address HOSTADDRESS
                        Address to host on (default: 127.0.0.1)
  -p PORT, --port PORT  Port to listen on (default: 9000)
  -c CONFIG, --config CONFIG
                        tbears configuration file path (default: ./tbears_server_config.json)
```

**Options**

| shorthand, Name | default                     | Description                                          |
| :-------------- | :-------------------------- | :--------------------------------------------------- |
| -h, --help      |                             | show this help message and exit                      |
| -a, --address   | 127.0.0.1                   | IP address that the T-Bears service will host on.    |
| -p, --port      | 9000                        | Port number that the T-Bears service will listen on. |
| -c, --config    | ./tbears_server_config.json | T-Bears configuration file path                      |

#### tbears stop

**Description**

Stop all running SCOREs and T-Bears service.

**Usage**

```bash
usage: tbears stop [-h]

Stop all running SCOREs and tbears service

optional arguments:
  -h, --help  show this help message and exit
```

**Options**

| shorthand, Name | default | Description                     |
| :-------------- | :------ | :------------------------------ |
| -h, --help      |         | show this help message and exit |

#### tbears clear

**Description**

Clear all SCOREs deployed on local T-Bears service.

**Usage**

```bash
usage: tbears clear [-h]

Clear all SCOREs deployed on local tbears service

optional arguments:
  -h, --help  show this help message and exit
```

**Options**

| shorthand, Name | default | Description                     |
| :-------------- | :------ | :------------------------------ |
| -h, --help      |         | show this help message and exit |

#### tbears sync_mainnet

**Description**

Synchronize revision and governance SCORE with the mainnet

**Usage**

```bash
usage: tbears sync_mainnet [-h]

Synchronize revision and governance SCORE with the mainnet

optional arguments:
  -h, --help  show this help message and exit
```

**Options**

| shorthand, Name | default | Description                     |
| :-------------- | :------ | :------------------------------ |
| -h, --help      |         | show this help message and exit |

### T-Bears utility commands

Commands that generate configuration file and keystore file.

#### tbears keystore

**Description**

Create a keystore file in the given path. Generate a private and public key pair

**Usage**

```bash
usage: tbears keystore [-h] [-p PASSWORD] path

Create keystore file in the specified path. Generate privatekey, publickey
pair

positional arguments:
  path                  Path of keystore file.

optional arguments:
  -h, --help            show this help message and exit
  -p PASSWORD, --password PASSWORD
                        Keystore file's password
```

**Options**

| shorthand, Name | default | Description                              |
| :-------------- | :------ | :--------------------------------------- |
| path            |         | a keystore file path that is to be generated |
| -h, --help      |         | show this help message and exit          |
| -p, --password  |         | Keystore file's password                 |

**Examples**

```bash
(work) $ tbears keystore keystore_file
Input your keystore password:
Retype your keystore password:
Made keystore file successfully
```

#### tbears keyinfo
**Description**

Show a keystore information(address, privateKey, publicKey) in the specified path.  

**Usage**
```bash
usage: tbears keyinfo [-h] [-p PASSWORD] [--private-key] path

Show a keystore information(address, privateKey, publicKey) in the specified
path. If you want to get privateKey, input --private-key option

positional arguments:
  path                  Path of keystore file.

optional arguments:
  -h, --help            show this help message and exit
  -p PASSWORD, --password PASSWORD
                        Keystore file's password
  --private-key         option that whether show privateKey
```

**Options**

| shorthand, Name | default | Description                              |
| :-------------- | :------ | :--------------------------------------- |
| path            |         | a keystore file path that is to be shown |
| -h, --help      |         | show this help message and exit          |
| -p, --password  |         | Keystore file's password                 |
| --private-key   |         | option that whether show privateKey      |

**Examples**

```bash
(work) $ tbears keyinfo keystore
Input your keystore password:
{
    "address": "hxef73db5d0ad02eb1fadb37d0041be96bfa56d4e6",
    "publicKey": "0x040d60ccc4fd29307304a8e84715e6e1a2e643bcff14fbf90d9099dfc84585a6f6f0b6944594efebe433a12a005ba56d215d6e51697a3360b5d741f8db89955c66"
}

(work) $ tbears keyinfo --private-key keystore
Input your keystore password:
{
    "address": "hxef73db5d0ad02eb1fadb37d0041be96bfa56d4e6",
    "publicKey": "0x040d60ccc4fd29307304a8e84715e6e1a2e643bcff14fbf90d9099dfc84585a6f6f0b6944594efebe433a12a005ba56d215d6e51697a3360b5d741f8db89955c66",
    "privateKey": "54483cf6c525f831da699d73d273e48aa88c963ed5ac485b207c7bf4a57ddce1"
}
```

#### tbears genconf

**Description**

Generate T-Bears config files and keystore files.

```bash
usage: tbears genconf [-h]

Generate T-Bears config files and keystore files.

optional arguments:
  -h, --help  show this help message and exit
```

**Options**

| shorthand, Name | default | Description                     |
| :-------------- | :------ | :------------------------------ |
| -h, --help      |         | show this help message and exit |

**Examples**

```bash
(work) $ tbears genconf
Made tbears_cli_config.json, tbears_server_config.json, ./keystore/* successfully
```


### T-Bears SCORE commands

These commands are related to SCORE development and execution.  `tbears init` generates SCORE projects. `tbears deploy`,  `tbears sendtx` and `tbears call` commands are used to deploy the SCORE, send a transaction, and call a function.

#### tbears init

**Description**

Initialize SCORE development environment. Generate <project\>.py, package.json and test code in <project\> directory. The name of the SCORE class is \<scoreClass\>.  Default configuration files, "tbears_server_config.json" used when starting T-Bears and "tbears_cli_config.json" used when deploying SCORE, are also generated.

**Usage**

```bash
usage: tbears init [-h] project scoreClass

Initialize SCORE development environment. Generate <project>.py, package.json
and test code in <project> directory. The name of the score class is
<scoreClass>.

positional arguments:
  project     Project name
  scoreClass  SCORE class name

optional arguments:
  -h, --help  show this help message and exit
```

**Options**

| shorthand, Name | default | Description                     |
| :-------------- | :------ | :------------------------------ |
| project         |         | Project name                    |
| scoreClass      |         | SCORE class name                |
| -h, --help      |         | show this help message and exit |

**Examples**

```bash
(work) $ tbears init hello HelloWorld
Initialized hello successfully
(work) $ ls hello
__init__.py  hello.py  package.json  tests
```

**File description**

| **Item**                   | **Description**                                              |
| :------------------------- | :----------------------------------------------------------- |
| tbears_server_config.json  | T-Bears default configuration file will be created on the working directory. |
| tbears_cli_config.json     | Configuration file for CLI commands will be created on the working directory. |
| keystore/*                 | Keystore file for test account and P-Reps. |
| \<project>                 | SCORE project name. Project directory is created with the same name. |
| \<project>/\_\_init\_\_.py | \_\_init\_\_.py file to make the project directory recognized as a python package. |
| \<project>/package.json    | Contains the information needed when SCORE is loaded. <br> "main_module" and "main_class" should be specified. |
| \<project>/<project>.py    | SCORE main file, where `scoreClass` is defined.             |
| \<project>/tests           | Directory for SCORE test code.                              |
| \<project>/tests/\_\_init\_\_.py | \_\_init\_\_.py file to make the test directory recognized as a python package. |
| \<project>/tests/test\_<project>.py    | SCORE test main file.                              |

#### tbears deploy

**Description**

Deploy the SCORE. You can deploy it on local T-Bears service or on ICON network.

"tbears_cli_config.json" file contains the deployment configuration properties. (See below 'Configuration Files' chapter). If you want to use other configuration file, you can specify the file location with the '-c' option.

**Usage**

```bash
usage: tbears deploy [-h] [-u URI] [-t {tbears,zip}] [-m {install,update}]
                     [-f FROM] [-o TO] [-k KEYSTORE] [-n NID] [-p PASSWORD]
                     [-s STEPLIMIT] [-c CONFIG]
                     project

Deploy the SCORE

positional arguments:
  project               Project directory path or zip file path

optional arguments:
  -h, --help            show this help message and exit
  -u URI, --node-uri URI
                        URI of node (default: http://127.0.0.1:9000/api/v3)
  -t {tbears,zip}, --type {tbears,zip}
                        This option is deprecated since version 1.0.5. Deploy
                        command supports zip type only
  -m {install,update}, --mode {install,update}
                        Deploy mode (default: install)
  -f FROM, --from FROM  From address. i.e. SCORE owner address
  -o TO, --to TO        To address. i.e. SCORE address
  -k KEYSTORE, --key-store KEYSTORE
                        Keystore file path. Used to generate "from" address
                        and transaction signature
  -n NID, --nid NID     Network ID
  -p PASSWORD, --password PASSWORD
                        keystore file's password
  -s STEPLIMIT, --step-limit STEPLIMIT
                        Step limit
  -c CONFIG, --config CONFIG
                        deploy config path (default: ./tbears_cli_config.json)
```

**Options**

| shorthand, Name                                 | default                      | Description                                                  |
| :---------------------------------------------- | :--------------------------- | :----------------------------------------------------------- |
| project                                         |                              | Project directory or zip file which contains the SCORE package. If you want to deploy with a zip file, zip the project directory |
| -h, --help                                      |                              | show this help message and exit                              |
| -u, --node-uri                                  | http://127.0.0.1:9000/api/v3 | URI of node                                                  |
| -t {tbears,zip}, --type {tbears,zip}            |                              | This option is deprecated since version 1.0.5. Deploy command supports zip type only |
| -m {install,update},<br>--mode {install,update} | install                      | Deploy mode ("install" or "update").                         |
| -f, --from                                      |                              | From address. i.e. SCORE owner address. It is ignored if keystore is set |
| -o, --to                                        |                              | To address. i.e. SCORE address <br>This parameter is required when updating SCORE. |
| -k, --key-store                                 |                              | Keystore file path for SCORE owner                               |
| -n, --nid                                       |                              | Network ID of node. <br>Each network has unique ID. If the Network ID does not match, node will reject the SCORE. Network ID will be announced when a network opens to public.<br>0x3 is reserved for T-Bears service. However, T-Bears service does not verify the Network ID. |
| -p, --password                                  |                              | Password of keystore file |
| -s, --step-limit                                | an estimated Step            | Step limit of the transaction |
| -c, --config                                    | ./tbears_cli_config.json     | Configuration file path                                      |

**Examples**

```bash
# you can deploy a SCORE to the local T-Bears server without verifying signature
(work) $ tbears deploy hello

# when you deploy a SCORE to ICON, you need to specify the keystore file
# config.json should contain valid parameters like node-uri, nid, etc.
(work) $ tbears deploy hello -k keystore -c config.json
Input your keystore password:
Send deploy request successfully.
If you want to check SCORE deployed successfully, execute txresult command
transaction hash: 0x9c294b9608d9575f735ec2e2bf52dc891d7cca6a2fa7e97aee4818325c8a9d41

# when you update the SCORE 'hello', you need to specify the SCORE address with the '-o' option
(work) $ tbears deploy hello -m update -o cx6bd390bd855f086e3e9d525b46bfe24511431532 -k keystore -c config.json
Input your keystore password:
Send deploy request successfully.
If you want to check SCORE deployed successfully, execute txresult command
transaction hash: 0xad292b9608d9575f735ec2ebbf52dc891d7cca6a2fa7e97aee4818325c80934d
```

T-Bears can supply some required fields on behalf of the sender when those are not specified in the configuration file.
T-Bears will generate a valid JSON request using the following rules.

| Field name  | Description |
| :---------- | :---------- |
| `stepLimit` | The estimated Step usage ([debug_estimateStep] API is used) will be set for the transaction |
| `timestamp` | The current time will be set |



#### tbears test

**Description**

Run the unittest in the project.

**Usage**

```bash
usage: tbears test [-h] project

Run the unittest in the project

positional arguments:
  project     Project directory path

optional arguments:
  -h, --help  show this help message and exit
```

**Options**

| shorthand, Name | default                      | Description                                                  |
| :-------------- | :--------------------------- | :----------------------------------------------------------- |
| project         |                              | Project directory which contains the SCORE package and test code.|
| -h, --help      |                              | show this help message and exit                              |

**Examples**

```bash
(work) $ tbears test hello
..
----------------------------------------------------------------------
Ran 2 tests in 0.172s

OK
```

#### tbears sendtx

**Description**

Request `icx_sendTransaction` with the specified json file.

```bash
usage: tbears sendtx [-h] [-u URI] [-k KEYSTORE] [-c CONFIG] [-p PASSWORD]
                     [-s STEPLIMIT]
                     json_file

Request `icx_sendTransaction` with the specified json file and keystore file. If
keystore file is not given, tbears sends request as it is in the json file.

positional arguments:
  json_file             File path containing icx_sendTransaction content

optional arguments:
  -h, --help            show this help message and exit
  -u URI, --node-uri URI
                        URI of node (default: http://127.0.0.1:9000/api/v3)
  -k KEYSTORE, --key-store KEYSTORE
                        Keystore file path. Used to generate "from"address and
                        transaction signature
  -c CONFIG, --config CONFIG
                        Configuration file path. This file defines the default
                        value for the "uri" (default:
                        ./tbears_cli_config.json)
  -p PASSWORD, --password PASSWORD
                        Keystore file's password
  -s STEPLIMIT, --step-limit STEPLIMIT
                        Step limit
```

**Options**

| shorthand, Name | default                      | Description                                                  |
| :-------------- | :--------------------------- | :----------------------------------------------------------- |
| json_file       |                              | Path to the json file containing the request object for icx_transaction. |
| -h, --help      |                              | show this help message and exit                              |
| -u, --node-uri  | http://127.0.0.1:9000/api/v3 | URI of node                                                  |
| -k, --key-store |                              | Keystore file path. Used to generate transaction signature.  |
| -p, --password  |                              | Password of keystore file                                    |
| -s, --step-limit| an estimated Step            | Step limit of the transaction                                |
| -c, --config    | ./tbears_cli_config.json     | Configuration file path. This file defines the default values for the properties "keyStore", "uri" and "from". |

**Examples**

```bash
(work) $ cat send.json
{
  "jsonrpc": "2.0",
  "method": "icx_sendTransaction",
  "params": {
    "version": "0x3",
    "from": "hxef73db5d0ad02eb1fadb37d0041be96bfa56d4e6",
    "to": "cx4d5a79f329adcf00a3daa99539f0eeea2d43d239",
    "nid": "0x3",
    "dataType": "call",
    "data": {
      "method": "setValue",
      "params": {
        "value": "0x123"
      }
    }
  }
}

(work) $ tbears sendtx send.json -k keystore
Input your keystore password:
Send transaction request successfully.
transaction hash: 0xc8a3e3f77f21f8f1177d829cbc4c0ded6fd064cc8e42ef309dacff5c0a952289
```

T-Bears can supply some required fields on behalf of the sender when those are not specified in the `json_file`.
In the example above, `stepLimit` and `timestamp` fields are not specified, but T-Bears can make a valid JSON request using the following rules.

| Field name  | Description |
| :---------- | :---------- |
| `stepLimit` | The estimated Step usage ([debug_estimateStep] API is used) will be set for the transaction |
| `timestamp` | The current time will be set |



#### tbears call

**Description**

Request `icx_call` with the specified json file.

```bash
usage: tbears call [-h] [-u URI] [-c CONFIG] json_file

Request icx_call with the specified json file.

positional arguments:
  json_file             File path containing icx_call content

optional arguments:
  -h, --help            show this help message and exit
  -u URI, --node-uri URI
                        URI of node (default: http://127.0.0.1:9000/api/v3)
  -c CONFIG, --config CONFIG
                        Configuration file path. This file defines the default
                        value for the "uri" (default: ./tbears_cli_config.json)
```

**Options**

| shorthand, Name | default                      | Description                                                  |
| :-------------- | :--------------------------- | :----------------------------------------------------------- |
| json_file       |                              | Path to the json file containing the request object for icx_call |
| -h, --help      |                              | Show this help message and exit                              |
| -u, --node-uri  | http://127.0.0.1:9000/api/v3 | URI of node                                                  |
| -c, --config    | ./tbears_cli_config.json     | Configuration file path. This file defines the default values for the properties "keyStore", "uri" and "from". |

**Examples**

```bash
(work) $ cat call.json
{
  "jsonrpc": "2.0",
  "method": "icx_call",
  "params": {
    "to": "cx53d5080a7d8a805bb10eb9bc64637809dc910832",
    "dataType": "call",
    "data": {
      "method": "hello"
    }
  },
  "id": 1
}
(work) $ tbears call call.json
response : {
    "jsonrpc": "2.0",
    "result": "Hello",
    "id": 1
}
```

#### tbears scoreapi

**Description**

Get list of APIs that the given SCORE provides. Please refer to `icx_getScoreApi` of [ICON JSON-RPC API v3](https://github.com/icon-project/icon-rpc-server/blob/master/docs/icon-json-rpc-v3.md#icx_getscoreapi) for details.

**Usage**

```bash
usage: tbears scoreapi [-h] [-u URI] [-c CONFIG] address

Get SCORE's API using given SCORE address

positional arguments:
  address                  SCORE address to query SCORE API

optional arguments:
  -h, --help            show this help message and exit
  -u URI, --node-uri URI
                        URI of node (default: http://127.0.0.1:9000/api/v3)
  -c CONFIG, --config CONFIG
                        Configuration file path. This file defines the default
                        value for the "uri" (default: ./tbears_cli_config.json)
```

**Options**

| shorthand, Name | default                      | Description                                                  |
| :-------------- | :--------------------------- | :----------------------------------------------------------- |
| address         |                              | SCORE address to query APIs                                  |
| -h, --help      |                              | show this help message and exit                              |
| -u, --node-uri  | http://127.0.0.1:9000/api/v3 | URI of node.                                                 |
| -c, --config    | ./tbears_cli_config.json     | Configuration file path. This file defines the default value for the "uri". |

**Examples**

```bash
(work) $ tbears scoreapi cx0123456789abcdef0123456789abcdefabcdef12
SCORE API: [
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
    },
    {
        "type": "function",
        "name": "setValue",
        "inputs": [
            {
                "name": "value",
                "type": "int"
            }
        ],
        "outputs": []
    }
]
```


### T-Bears other commands

Commands that are related to ICX coin, transaction, and block.

#### tbears transfer

**Description**

Transfer designated amount of ICX coins.

**Usage**

```bash
usage: tbears transfer [-h] [-f FROM] [-k KEYSTORE] [-n NID] [-u URI]
                       [-p PASSWORD] [-s STEPLIMIT] [-c CONFIG]
                       to value

Transfer ICX coin.

positional arguments:
  to                    Recipient
  value                 Amount of ICX coin in loop to transfer (1 icx = 1e18
                        loop)

optional arguments:
  -h, --help            show this help message and exit
  -f FROM, --from FROM  From address.
  -k KEYSTORE, --key-store KEYSTORE
                        Keystore file path. Used to generate "from" address
                        and transaction signature
  -n NID, --nid NID     Network ID (default: 0x3)
  -u URI, --node-uri URI
                        URI of node (default: http://127.0.0.1:9000/api/v3)
  -p PASSWORD, --password PASSWORD
                        Keystore file's password
  -s STEPLIMIT, --step-limit STEPLIMIT
                        Step limit
  -c CONFIG, --config CONFIG
                        Configuration file path. This file defines the default
                        values for the properties "keyStore", "uri", "from"
                        and "stepLimit". (default: ./tbears_cli_config.json)
```

**Options**

| shorthand, Name | default                      | Description                                                  |
| :-------------- | :--------------------------- | :----------------------------------------------------------- |
| to              |                              | Recipient address.                                           |
| value           |                              | Amount of ICX coin in loop to transfer to "to" address. (1 icx = 1e18 loop) |
| -h, --help      |                              | show this help message and exit                              |
| -f, --from      |                              | From address. It is ignored if keystore is set            |
| -k, --key-store |                              | Keystore file path. Used to generate "from" address and transaction signature. |
| -u, --node-uri  | http://127.0.0.1:9000/api/v3 | URI of node                                                  |
| -n, --nid       | 0x3                          | Network ID                                                   |
| -p, --password  |                              | Password of keystore file                                    |
| -s, --step-limit| an estimated Step            | Step limit of the transaction                                |
| -c, --config    | ./tbears_cli_config.json     | Configuration file path. This file defines the default values for the properties "keyStore", "uri" and "from". |

**Examples**

```bash
(work) $ tbears transfer -k test_keystore hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab 1e18
Send transfer request successfully.
transaction hash: 0xc1b92b9a08d8575f735ec2ebbf52dc831d7c2a6a2fa7e97aee4818325cad919e
```

#### tbears balance

**Description**

Get balance of given address.

**Usage**

```bash
usage: tbears balance [-h] [-u URI] [-c CONFIG] address

Get balance of given address in loop unit

positional arguments:
  address               Address to query the ICX balance

optional arguments:
  -h, --help            show this help message and exit
  -u URI, --node-uri URI
                        URI of node (default: http://127.0.0.1:9000/api/v3)
  -c CONFIG, --config CONFIG
                        Configuration file path. This file defines the default
                        value for the "uri" (default: ./tbears_cli_config.json)

```

**Options**

| shorthand, Name | default                      | Description                                                  |
| :-------------- | :--------------------------- | :----------------------------------------------------------- |
| address         |                              | Address to query the ICX balance                             |
| -h, --help      |                              | show this help message and exit                              |
| -u, --node-uri  | http://127.0.0.1:9000/api/v3 | URI of node                                                  |
| -c, --config    | ./tbears_cli_config.json     | Configuration file path. This file defines the default value for the "uri". |

**Examples**

```bash
(work) $ tbears balance hx0123456789abcdef0123456789abcdefabcdef12
balance in hex: 0x2961fff8ca4a62327800000
balance in decimal: 800460000000000000000000000
```

#### tbears totalsupply

**Description**

Query total supply of ICX.

**Usage**

```bash
usage: tbears totalsupply [-h] [-u URI] [-c CONFIG]

Query total supply of ICX in loop unit

optional arguments:
  -h, --help            show this help message and exit
  -u URI, --node-uri URI
                        URI of node (default: http://127.0.0.1:9000/api/v3)
  -c CONFIG, --config CONFIG
                        Configuration file path. This file defines the default
                        value for the "uri" (default: ./tbears_cli_config.json)
```

**Options**

| shorthand, Name | default                      | Description                                                  |
| :-------------- | :--------------------------- | :----------------------------------------------------------- |
| -h, --help      |                              | show this help message and exit                              |
| -u, --node-uri  | http://127.0.0.1:9000/api/v3 | URI of node                                                  |
| -c, --config    | ./tbears_cli_config.json     | Configuration file path. This file defines the default value for the "uri". |

**Examples**

```bash
(work) $ tbears totalsupply
Total supply of ICX in hex: 0x2961fff8ca4a62327800000
Total supply of ICX in decimal: 800460000000000000000000000
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
                        Configuration file path. This file defines the default
                        value for the "uri" (default: ./tbears_cli_config.json)
```

**Options**

| shorthand, Name | default                      | Description                                                  |
| :-------------- | :--------------------------- | :----------------------------------------------------------- |
| hash            |                              | Hash of the transaction to be queried                        |
| -h, --help      |                              | show this help message and exit                              |
| -u, --node-uri  | http://127.0.0.1:9000/api/v3 | URI of node                                                  |
| -c, --config    | ./tbears_cli_config.json     | Configuration file path. This file defines the default value for the "uri". |

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

#### tbears txbyhash

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
                        Configuration file path. This file defines the default
                        value for the "uri" (default: ./tbears_cli_config.json)
```

**Options**

| shorthand, Name | default                      | Description                                                  |
| :-------------- | :--------------------------- | :----------------------------------------------------------- |
| hash            |                              | Hash of the transaction to be queried                        |
| -h, --help      |                              | show this help message and exit                              |
| -u, --node-uri  | http://127.0.0.1:9000/api/v3 | URI of node                                                  |
| -c, --config    | ./tbears_cli_config.json     | Configuration file path. This file defines the default value for the "uri". |

**Examples**

```bash
(work) $ tbears txbyhash 0x95be9f0247bc3b7ed07fe07c53613c580642ef991c574c85db45dbac9e8366df

Transaction: {
    "jsonrpc": "2.0",
    "result": {
        "version": "0x3",
        "from": "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "value": "0x0",
        "stepLimit": "0x3000000",
        "timestamp": "0x572e8fd95db26",
        "nid": "0x3",
        "nonce": "0x1",
        "to": "cx0000000000000000000000000000000000000000",
        "data": {
            "contentType": "application/zip",
            "content": "0x32b34cfa39993fa093e",
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



#### tbears lastblock

**Description**

Query last block info. When running on T-Bears service, "merkle_tree_root_hash" and "signature" will be empty.

**Usage**

```bash
usage: tbears lastblock [-h] [-u URI] [-c CONFIG]

Get last block info

optional arguments:
  -h, --help            show this help message and exit
  -u URI, --node-uri URI
                        URI of node (default: http://127.0.0.1:9000/api/v3)
  -c CONFIG, --config CONFIG
                        Configuration file path. This file defines the default
                        value for the "uri" (default: ./tbears_cli_config.json)
```

**Options**

| shorthand, Name | default                      | Description                                                  |
| :-------------- | :--------------------------- | :----------------------------------------------------------- |
| -h, --help      |                              | show this help message and exit                              |
| -u, --node-uri  | http://127.0.0.1:9000/api/v3 | URI of node                                                  |
| -c, --config    | ./tbears_cli_config.json     | Configuration file path. This file defines the default value for the "uri". |

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
                "stepLimit": "0x3000000",
                "timestamp": "0x572e8fd95db26",
                "nid": "0x3",
                "nonce": "0x1",
                "to": "cx0000000000000000000000000000000000000000",
                "data": {
                    "contentType": "application/zip",
                    "content": "0x32b34cfa39993fa093e",
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

#### tbears blockbyheight

**Description**

Get block info using given block height.

**Usage**

```bash
usage: tbears blockbyheight [-h] [-u URI] [-c CONFIG] height

Get block info using given block height

positional arguments:
  height                  height of the block to be queried

optional arguments:
  -h, --help            show this help message and exit
  -u URI, --node-uri URI
                        URI of node (default: http://127.0.0.1:9000/api/v3)
  -c CONFIG, --config CONFIG
                        Configuration file path. This file defines the default
                        value for the "uri" (default: ./tbears_cli_config.json)
```

**Options**

| shorthand, Name | default                      | Description                                                  |
| :-------------- | :--------------------------- | :----------------------------------------------------------- |
| height          |                              | Height of the block to be queried                            |
| -h, --help      |                              | show this help message and exit                              |
| -u, --node-uri  | http://127.0.0.1:9000/api/v3 | URI of node                                                  |
| -c, --config    | ./tbears_cli_config.json     | Configuration file path. This file defines the default value for the "uri". |

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

#### tbears blockbyhash

**Description**

Get block info using given block hash.

**Options**

| shorthand, Name | default                      | Description                                                  |
| :-------------- | :--------------------------- | :----------------------------------------------------------- |
| hash            |                              | Hash of the block to be queried                              |
| -h, --help      |                              | show this help message and exit                              |
| -u, --node-uri  | http://127.0.0.1:9000/api/v3 | URI of node                                                  |
| -c, --config    | ./tbears_cli_config.json     | Configuration file path. This file defines the default value for the "uri". |

**Usage**

```bash
usage: tbears blockbyhash [-h] [-u URI] [-c CONFIG] hash

Get block info using given block hash

positional arguments:
  hash                  hash of the block to be queried

optional arguments:
  -h, --help            show this help message and exit
  -u URI, --node-uri URI
                        URI of node (default: http://127.0.0.1:9000/api/v3)
  -c CONFIG, --config CONFIG
                        Configuration file path. This file defines the default
                        value for the "uri" (default: ./tbears_cli_config.json)
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



### tbears console

**Description**

Enter T-Bears interactive mode using IPython. ([Ipython.org](https://ipython.org/))

**Usage**

```bash
usage: tbears console [-h]


Get into tbears interactive mode by embedding IPython

optional arguments:
  -h, --help  show this help message and exit
```

**Examples**

In the interactive mode, you can execute command in short form (without `tbears`) by predefined IPython's magic command.
TAB will complete T-Bears's command or variable names. Use TAB.

```bash
(work) $ tbears console
tbears) start
Started tbears service successfully
...

tbears) balance hxef73db5d0ad02eb1fadb37d0041be96bfa56d4e6

balance : 0x0
```
In IPython, you can access previous output using "_" expression.

```bash
tbears) pwd
'/Users/username/working/'

tbears) _
'/Users/username/working/'
```

You can access nth-output using _n-th expression.
The `Out` object is a dictionary mapping input numbers to their outputs.

```bash
tbears) '1'
'1'

tbears) 'second'
'second'

tbears) 3
3

tbears) _2
'second'

tbears) Out
{1: '1', 2: 'second', 3: 3, 4: 'second'}
```

You can pass the value of a variable as an argument by prefixing the variable name with "$".

```bash
tbears) address = f"hx{'0'*40}"

tbears) balance $address

balance : 0x2961fff8ca4a62327800000
```

You should use "{}" expression when you pass a member of list or dictionary.

```bash
tbears) deploy sample_token

Send deploy request successfully.
transaction hash: 0x541d8c9d3e12d92ad50897f81178301f21650b0b48dd5cc722b28b5c56cbc29a


tbears) txresult {_['result']}

{'jsonrpc': '2.0',
 'result': {'txHash': '0xd1ee48aa5d26c1deb275da644e4ffe607c9e556474403c51040dfa59b0dd563c',
  'blockHeight': '0x3',
...

```

In the interactive mode, `deployresults` command is available to list up the SCOREs that have been deployed while T-Bears interactive mode is running.
```bash
tbears) deployresults
1.path : hello/, txhash : 0x583a89ec656d71d1641945a39792e016eefd6221ad536f9c312957f0c4336774, deployed in : http://127.0.0.1:9000/api/v3
2.path : token/, txhash : 0x8c2fe3c877d46b7a1ba7feb117d0b12c8b88f33517ad2315ec45e8b7223c22f8, deployed in : http://127.0.0.1:9000/api/v3
3.path : abctoken/, txhash : 0xee6e311d2652fd5ed5981f4906bca5d4d6933400721fcbf3528249d7bf460e42, deployed in : http://127.0.0.1:9000/api/v3

```

T-Bears assigns T-Bears command execution result to '_r' variable.

```bash

tbears) deploy sample_token
Send deploy request successfully.
transaction hash: 0x5257b44fe0f36c492e255dbfcdb2ca1134dc9a942b875241d01db3d36ac2bdc8

tbears) result = _r

tbears) result
{'jsonrpc': '2.0',
 'result': '0x5257b44fe0f36c492e255dbfcdb2ca1134dc9a942b875241d01db3d36ac2bdc8',
 'id': 1}

tbears) txresult {result['result']}
Transaction result: {
    "jsonrpc": "2.0",
    "result": {
        "txHash": "0x5257b44fe0f36c492e255dbfcdb2ca1134dc9a942b875241d01db3d36ac2bdc8",
        "blockHeight": "0x1",
        "blockHash": "9c06e5c1bbd8ed1efc1ec7d1be59b64dd102bde43fc13c3f22e25e5aaa1eda51",
        "txIndex": "0x0",
        "to": "cx0000000000000000000000000000000000000000",
        "scoreAddress": "cxb8f2c9ba48856df2e889d1ee30ff6d2e002651cf",
...

tbears) scoreapi {_r['result']['scoreAddress']}
SCORE API: [
    {
        "type": "fallback",
        "name": "fallback",
        "inputs": []
    },
...

```

### Configuration Files

#### tbears_server_config.json

When starting T-Bears (`tbears start`), `tbears_server_config.json` is used to configure the parameters and initial settings.

```json
{
    "hostAddress": "127.0.0.1",
    "port": 9000,
    "scoreRootPath": "./.score",
    "stateDbRootPath": "./.statedb",
    "log": {
        "logger": "tbears",
        "level": "info",
        "filePath": "./tbears.log",
        "colorLog": true,
        "outputType": "file",
        "rotate": {
            "type": "bytes",
            "maxBytes": 10485760,
            "backupCount": 10
        }
    },
    "service": {
        "fee": false,
        "audit": false,
        "deployerWhiteList": false
    },
    "genesis": {
        "nid": "0x3",
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
            },
            {
                "name": "test1",
                "address": "hxe7af5fcfd8dfc67530a01a0e403882687528dfcb",
                "balance": "0x2961fff8ca4a62327800000"
            }
        ]
    },
    "blockConfirmInterval": 2,
    "blockConfirmEmpty": true,
    "mainPRepCount": 4,
    "iissCalculatePeriod": 30,
    "termPeriod": 30
}
```

| Field           | Data type | Description                                                  |
| :-------------- | :-------- | :----------------------------------------------------------- |
| hostAddress     | string    | IP address that T-Bears service will listen on.              |
| port            | int       | Port number that T-Bears service will listen on.             |
| scoreRootPath   | string    | Root directory where SCORE will be installed.                |
| stateDbRootPath | string    | Root directory where state DB file will be created.          |
| log             | dict      | T-Bears log setting                                          |
| log.logger      | string    | Main logger in process                                       |
| log.level       | string    | log level. <br/>"debug", "info", "warning", "error"          |
| log.filePath    | string    | Log file path.                                               |
| log.colorLog    | boolean   | Log display option (color or black)                          |
| log.outputType  | string    | “console”: log outputs to the console that T-Bears is running.<br/>“file”: log outputs to the file path.<br/>“console&#124;file”: log outputs to both console and file. |
| log.rotate      | dict      | Log rotate setting                                           |
| log.rotate.type | string    | "peroid": rotate by period.<br/>"bytes": rotate by maxBytes.<br/>"period&#124;bytes": log rotate to both period and bytes. |
| log.rotate.period         | string    | use logging.TimedRotatingFileHandler 'when'<br/> ex) daily, weekly, hourly or minutely |
| log.rotate.interval       | string    | use logging.TimedRotatingFileHandler 'interval'<br/> ex) (period: hourly, interval: 24) == (period: daily, interval: 1)|
| log.rotate.maxBytes       | integer   | use logging.RotatingFileHandler 'maxBytes'<br/> ex) 10mb == 10 * 1024 * 1024 |
| log.rotate.backupCount    | integer   | limit log file count                                         |
| service                   | didct     | T-Bears service setting                                       |
| service.fee               | boolean   | true &#124; false. Charge a fee per transaction when enabled     |
| service.audit             | boolean   | true &#124; false. Audit deploy transactions when enabled        |
| service.deployerWhiteList | boolean   | true &#124; false. Limit SCORE deploy permission when enabled    |
| genesis                   | dict      | Genesis information of T-Bears node.                          |
| genesis.nid               | string    | Network ID.                                                  |
| genesis.accounts          | list      | List of accounts that holds initial coins. <br>(index 0) genesis: account that holds initial coins.<br>(index 1) fee_treasury: account that collects transaction fees.<br>(index 2~): test accounts that you can add. |
| channel                   | string    | channel name interact with iconrpcserver and iconservice     |
| amqpKey                   | string    | amqp key name interact with iconrpcserver and iconservice    |
| amqpTarget                | string    | amqp target name interact with iconrpcserver and iconservice |
| blockConfirmInterval      | integer   | Confirm block every N seconds |
| blockConfirmEmpty         | boolean   | true &#124; false. Confirm empty block when enabled              |
| mainPRepCount             | integer   | IISS main P-Rep count |
| termPeriod                | integer   | Term of main P-Rep |

#### tbears_cli_config.json

For every T-Bears CLI commands except `start`, `stop`, `clear`, `init` and `keystore`, this file is used to configure the default parameters and initial settings.

In this configuration file, you can define default options values for some CLI commands. For example, SCORE's `on_install()` or `on_update()` method is called on deployment. You can set the deploy `mode` and the parameters (`scoreParams`) of `on_install()` or `on_update()` as shown below.

```json
{
    "uri": "http://127.0.0.1:9000/api/v3",
    "nid": "0x3",
    "keyStore": null,
    "from": "hxe7af5fcfd8dfc67530a01a0e403882687528dfcb",
    "to": "cx0000000000000000000000000000000000000000",
    "deploy": {
        "mode": "install",
        "scoreParams": {}
    },
    "txresult": {},
    "transfer": {}
}
```

| Field              | Data  type | Description                                                  |
| ------------------ | :--------- | :----------------------------------------------------------- |
| uri                | string     | URI to send the request.                                     |
| nid                | string     | Network ID. 0x3 is reserved for T-Bears.                     |
| keyStore           | string     | Keystore file path.                                          |
| from               | string     | From address. It is ignored if 'keyStore' is set.            |
| to                 | string     | To address.                                                  |
| stepLimit          | string     | (optional) stepLimit value.                                  |
| deploy             | dict       | Options for deploy command.                                  |
| deploy.mode        | string     | Deploy mode.<br>install: new SCORE deployment.<br>update: update the SCORE that was previously deployed. |
| deploy.scoreParams | dict       | Parameters to be passed to on_install() or on_update()       |
| deploy.from        | string     | Address of the SCORE deployer<br>Optional. This value will override "from" value. If not given, "from" value will be used. |
| deploy.to          | string     | Used when update SCORE (The address of the SCORE being updated).<br/>In the case of "install" mode, the address should be 'cx0000~'.<br>Optional. This value will override "to" value. If not given, "to" value will be used. |
| txresult           | dict       | Options for txresult command.<br>You can define command options in a dict. |
| transfer           | dict       | Options for transfer command.<br>You can define command options in a dict. |

Following CLI commands and options can be defined in the configuration file.

| Command  | Options                                                    |
| :------- | :--------------------------------------------------------- |
| deploy   | uri, nid, keyStore, from, to, mode, scoreParams, stepLimit |
| transfer | uri, nid, keyStore, from, stepLimit                        |
| sendtx   | uri, nid, keyStore, from, stepLimit                        |
| txresult<br>balance<br>totalsupply<br>scoreapi<br>txbyhash<br>lastblock<br>blockbyhash<br>blockbyheight<br>call<br>| uri |


#### keystore files

* keystore_test1
  Keystore file for the test account. Password of this keystore file is `test1_Account`.
  You can find the test account 'test1' in `tbears_server_config.json` and this test account has enough balance to test on local environment.

  **Do not transfer any ICX or tokens to 'test1' account.**

* prepN_keystore
  Keystore files for the main P-Rep. Password of these keystore files are `prepN_Account`.
  `sync_mainnet` command makes 4 main P-Reps and you can manage these 4 main P-Rep accounts with prepN_keystore files.

## References
- [ICON JSON-RPC API v3](https://github.com/icon-project/icon-rpc-server/blob/master/docs/icon-json-rpc-v3.md)
- [earlgrey](https://github.com/icon-project/earlgrey)
- [ICON Commons](https://github.com/icon-project/icon-commons)
- [ICON RPC Server](https://github.com/icon-project/icon-rpc-server)
- [ICON Service](https://github.com/icon-project/icon-service)
- [SCORE integration Test](https://github.com/icon-project/t-bears/blob/master/docs/score_integration_test.md)

[debug_estimateStep]: https://github.com/icon-project/icon-rpc-server/blob/master/docs/icon-json-rpc-v3.md#debug_estimatestep


## License

This project follows the Apache 2.0 License. Please refer to [LICENSE](https://www.apache.org/licenses/LICENSE-2.0) for details.
