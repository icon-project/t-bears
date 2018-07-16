

# ICON SCORE development tool (tbears) TUTORIAL

## Change history

| Date       | Version  | Author | Description                                                 |
| :--------- | :---- | :----: | :--------------------------------------------------- |
| 2018.07.16 | 0.9.3 | Soobok Jin | update tbears cli to enhanced version and modify entire document structure and translate into English. |
| 2018.07.10 | 0.9.3 | Chiwon Cho | earlgrey package description added. |
| 2018.07.06 | 0.9.3 | Inwon Kim | Configuration file updated.       |
| 2018.06.12 | 0.9.2 | Chiwon Cho | Tutorial moved from doc to markdown. |
| 2018.06.11 | 0.9.1 | Chiwon Cho | Error codes added. icx_getTransactionResult description updated. |
| 2018.06.01 | 0.9.0 | Chiwon Cho | JSON-RPC API v3 ChangeLog added. |

## tbears Overview
tbears is a suite of tools for SCORE dApp developers to develop and deploy SCORE.

it also provide SCORE base templete. This makes it easier to develop SCORE dApp.

## Installation

This guide will explain how to install the tbears onto your system. With the tbears, you can develop and deploy SCORE.

### requirements

ICON SCORE development and execution requires following environments.

* OS: MacOS, Linux
    * Windows are not supported yet.
* Python
    * Version: python 3.6+
    * IDE: Pycharm is recommended.

**library**

| name        | description                                                  | github                                                       |
| ----------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| LevelDB     | ICON SCORE uses levelDB open-source to store SCORE states.   | [LevelDB GitHub](https://github.com/google/leveldb)          |
| libSecp256k | ICON SCORE uses secp256k open-source to sign and validate signature. | [secp256k GitHub](https://github.com/bitcoin-core/secp256k1) |

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
(work) $ pip install iconservice-x.x.x-py3-none-any.whl
(work) $ pip install tbears-x.x.x-py3-none-any.whl
```

### Setup on Linux

```bash
#install levelDB
sudo apt-get install libleveldb1 libleveldb-dev
#install libSecp256k
sudo apt-get install libsecp256k1-dev

# Create a working directory
$ mkdir work
$ cd work

# setup the python virtualenv development environment
$ virtualenv -p python3 .
$ source bin/activate

# Install the ICON SCORE dev tools
(work) $ pip install earlgrey-x.x.x-py3-none-any.whl
(work) $ pip install iconservice-x.x.x-py3-none-any.whl
(work) $ pip install tbears-x.x.x-py3-none-any.whl
```

## how to use tbears

### Command-line interfaces(CLIs)

#### overview

tbears has 6 command, init, start, stop, deploy, clear, samples.

**usage**

```bash
usage: tbears [-h] [-d] {init,start,stop,deploy,clear,samples} ...

tbears v0.9.3 arguments

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           Debug mode

subcommands:
  If you want to see help message of subcommands, use "tbears subcommand -h"
  {init,start,stop,deploy,clear,samples}
    init                Initialize tbears project
    start               Start tbears serivce
    stop                Stop tbears service
    deploy              Deploy the SCORE
    clear               Clear all SCORE deployed on tbears service
    samples             Create two SCORE samples (sample_crowd_sale,
                        sample_token)
```

**options**

| shorthand, Name | default | Description                     |
| --------------- | :------ | ------------------------------- |
| -h, --help      |         | show this help message and exit |
| -d, --debug     |         | Debug mode                      |

#### tbears init

**description**

Initialize SCORE development environment. Generate \<project\>.py and package.json in <project\> directory. The name of the score class is \<score_class\>

**usage**

```bash
usage: tbears init [-h] project score_class
Initialize SCORE development environment. Generate <project>.py and
package.json in <project> directory. The name of the score class is
<score_class>.

positional arguments:
  project      Project name
  score_class  SCORE class name

optional arguments:
  -h, --help   show this help message and exit
```

**options**

| shorthand, Name | default | Description                     |
| --------------- | :------ | ------------------------------- |
| -h, --help      |         | show this help message and exit |

**examples**

```bash
(work) $ tbears init abc ABCToken
(work) $ ls abc
abc.py  __init__.py  package.json
```

**File description**

| **Item**                   | **Description**                                              |
| :------------------------- | :----------------------------------------------------------- |
| \<project>                 | SCORE project name. Project folder is create with the same name. |
| tbears.json                | tbears default configuration file will be created on the working directory. |
| \<project>/\_\_init\_\_.py | \_\_init\_\_.py file to make the project folder recognized as a python package. |
| \<project>/package.json    | SCORE metadata.                                              |
| \<project>/\<project>.py   | SCORE main file. ABCToken class is defined.                  |
| tests                      | not implemented                                              |

#### tbears start

**description**

start tbears service

**usage**

```bash
usage: tbears start [-h] [-a ADDRESS] [-p PORT] [-c CONFIG]

Start tbears service

optional arguments:
  -h, --help                       show this help message and exit
  -a ADDRESS, --address ADDRESS    Address to host on (default: 0.0.0.0)
  -p PORT, --port PORT             Listen port (default: 9000)
  -c CONFIG, --config CONFIG       tbears configuration file path(default:./tbears.json)
```

**options**

| shorthand, Name | default       | Description                     |
| --------------- | :------------ | ------------------------------- |
| -h, --help      |               | show this help message and exit |
| -a, --address   | 0.0.0.0       | Address to host on              |
| -p, --port      | 9000          | Listen port                     |
| -c, --config    | ./tbears.json | tbears configuration file path  |

#### tbears stop

**description**

Stop all running SCORE and tbears service

**usage**

```bash
usage: tbears stop [-h]

Stop all running SCORE and tbears service

optional arguments:
  -h, --help  show this help message and exit
```

**options**

| shorthand, Name | default | Description                     |
| --------------- | :------ | ------------------------------- |
| -h, --help      |         | show this help message and exit |

#### tbears deploy

**description**

Deploy the SCORE in project

**usage**

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
  -t {tbears,icon}, --type {tbears,icon}       Deploy SCORE type
                                               ("tbears" or "icon". default: tbears)
  -m {install,update}, --mode {install,update} Deploy mode
                                               ("install" or "update". default: update)
  -f FROM, --from FROM                         From address. i.e. SCORE owner address
  -o TO, --to TO                               To address. i.e. SCORE address
  -k KEYSTORE, --key-store KEYSTORE            Key store file for SCORE owner
  -c CONFIG, --config CONFIG                   deploy config path (default: ./deploy.json
```

**options**

| shorthand, Name                                 | default                      | Description                                                  |
| ----------------------------------------------- | :--------------------------- | ------------------------------------------------------------ |
| -h, --help                                      |                              | show this help message and exit                              |
| -u, --node-uri                                  | http://127.0.0.1:9000/api/v3 | URI of node                                                  |
| -t {tbears,icon},<br> --type {tbears,icon}      | tbears                       | Deploy SCORE type ("tbears" or "icon" ).                     |
| -m {install,update},<br>--mode {install,update} | install                      | Deploy mode ("install" or "update").                         |
| -f, --from                                      |                              | From address. i.e. SCORE owner address                       |
| -o, --to                                        |                              | To address. i.e. SCORE address <br>**(only when update score)** |
| -k, --key-store                                 |                              | Key store file for SCORE owner                               |
| -c, --config                                    | ./deploy.json                | deploy config path                                           |

**examples**

```bash
(Work)$ tbears deploy -t tbears abc

(work) $ cat ./deploy.json
{
    "deploy": {
        "uri": "http://127.0.0.1:9000/api/v3",
        "scoreType": "tbears",
        "mode": "install",
        "from": "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "to": "cx0000000000000000000000000000000000000000",
        "stepLimit": "0x12345",
        "scoreParams": {
        	"init_supply": "0x3e8",
        	"decimal": "0x12"
        }
    }
}
(work) $ tbears deploy abc -c ./deploy.json

#when you deploy SCORE to icon, input keystore password
(Work)$ tbears deploy -t icon -f hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa -k keystore abc
input your key store password:

#update abc SCORE
#append prefix 'cx' in front of score address
(Work)$ tbears deploy abc -m update -o cx6bd390bd855f086e3e9d525b46bfe24511431532
```

#### tbears clear

**description**

Clear all SCORE deployed on local tbears service

**usage**

```bas
usage: tbears clear [-h]

Clear all SCORE deployed on local tbears service

optional arguments:
  -h, --help  show this help message and exit json
```

**options**

| shorthand, Name | default | Description                     |
| --------------- | :------ | ------------------------------- |
| -h, --help      |         | show this help message and exit |

#### tbears samples

**description**

Create two SCORE samples (sample_crowd_sale, sample_token)

**usage**

```bash
usage: tbears samples [-h]

Create two SCORE samples (sample_crowd_sale, sample_token)

optional arguments:
  -h, --help  show this help message and exit
```

**options**

| shorthand, Name | default | Description                     |
| --------------- | :------ | ------------------------------- |
| -h, --help      |         | show this help message and exit |

**examples**

```bash
(work) $ tbears samples

(work) $ ls sample*
sample_crowd_sale:
__init__.py  package.json  sample_crowd_sale.py

sample_token:
__init__.py  package.json  __pycache__  sample_token.py
```

### configuration files

#### tbears configuration file

Load tbears.json file in the tbears working directory.

**tbears.json**

```json
{
    "hostAddress": "0.0.0.0",
    "port": 9000,
    "scoreRoot": "./.score",
    "dbRoot": "./.db",
    "enableFee": false,
    "enableAudit": false,
    "log": {
        "colorLog": true,
        "level": "debug",
        "filePath": "./tbears.log",
        "outputType": "console|file"
    },
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
```

| Field          | Data type | Description                                                  |
| :------------- | :-------- | :----------------------------------------------------------- |
| hostAddress    | string    | JSON-RPC server IP                                           |
| port           | int       | JSON-RPC server port number.                                 |
| scoreRoot      | string    | Root directory that SCORE will be installed.                 |
| dbRoot         | string    | Root directory that state DB file will be created.           |
| enableFee      | boolean   | not implemented                                              |
| enableAudit    | boolean   | not implemented                                              |
| log            | dict      | tbears logging setting                                       |
| log.colorLog   | boolean   | Log Display option(color or black)                           |
| log.level      | string    | log level. <br/>"debug", "info", "warning", "error"          |
| log.filePath   | string    | log file path.                                               |
| log.outputType | string    | “console”: log outputs to the console that tbears is running.<br/>“file”: log outputs to the file path.<br/>“console\|file”: log outputs to both console and file. |
| accounts       | list      | List of accounts that holds initial coins. <br>(index 0) genesis: account that holds initial coins.<br>(index 1) fee_treasury: account that collects transaction fees.<br>(index 2~): accounts. |

#### score deploy configuration file

**deploy.json(a separate file from tbears config)**

```json
{
    "deploy": {
        "uri": "http://127.0.0.1:9000/api/v3",
        "scoreType": "tbears",
        "mode": "install",
        "from": "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "to": "cx0000000000000000000000000000000000000000",
        "stepLimit": "0x12345",
        "scoreParams": {
        	"init_supply": "0x3e8",
        	"decimal": "0x12"
        }
    }
}
```

| Field             | Data  type | Description                                                  |
| ----------------- | :--------- | :----------------------------------------------------------- |
| deploy            | dict       | configuration when deploying SCORE                           |
| deploy.uri        | string     | uri to send request of deployment                            |
| deploy.scoreType  | string     | SCORE type to deploy (tbears or icon)                        |
| deploy.mode       | string     | deploy mode setting<br>install: new SCORE deployment<br>update: updates SCORE which is Previously deployed |
| deploy.from       | string     | address of SCORE deployer                                    |
| deploy.to         | string     | (optional) Used when update SCORE (The address of the SCORE being updated).<br/>(in the case of install mode, set 'cx0000~') |
| delploy.stepLimit | string     | -(optional)                                                  |
| scoreParams       | dict       | Parameters to be passed to on_install() or on_update()       |

## Utilities

This chapter explains the utilities that will help SCORE development.

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

* tbears currently does not have loopchain engine, so some JSON-RPC APIs which are not related to SCORE developement may not function.
    * Below JSON-RPC APIs are supported in tbears:
        * icx_getBalance, icx_getTotalSupply, icx_getBalance, icx_call, icx_sendTransaction, icx_getTransactionResult
* In next versions, tbears commands or SCORE development methods may change in part.
* For the development convinience, JSON-RPC server in tbears does not verify the transaction signature.

