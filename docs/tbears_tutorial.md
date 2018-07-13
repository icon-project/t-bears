

ICON SCORE 개발 도구(tbears) TUTORIAL

## 문서 이력

| 일시       | 버전  | 작성자 | 비고                                                 |
| :--------- | :---- | :----: | :--------------------------------------------------- |
| 2018.07.13 | 0.9.3 | 진수복 |                                                      |
| 2018.07.10 | 0.9.3 | 조치원 | earlgrey 패키지 설명 추가                            |
| 2018.07.06 | 0.9.3 | 김인원 | 설정 파일 내용 변경                                  |
| 2018.06.12 | 0.9.2 | 조치원 | Markdown 형식으로 변경                               |
| 2018.06.11 | 0.9.1 | 조치원 | 에러 코드표 추가, icx_getTransactionResult 내용 수정 |
| 2018.06.01 | 0.9.0 | 조치원 | JSON-RPC API v3 ChangeLog 추가                       |

## tbears Overview

TODO: tbears 정의 입력



## Installation

### requirements

TODO: MAC, Linux 설치 방법 각각 소개 & 구조 설계

현 시점에서 ICON SCORE 개발 및 실행을 위해서는 다음의 환경이 요구된다.

* OS: MacOS, Linux
    * 현재 Windows는 미지원
* Python
    * 버전: python 3.6 이상
    * IDE: Pycharm 권장



### LevelDB

ICON SCORE에서는 SCORE의 상태들을 저장하기 위해 levelDB 오픈소스를 사용한다.
ICON SCORE 개발 환경을 구축하기 위해서는 levelDB 개발 라이브러리의 사전 설치가 반드시 필요하다.<br/>
[LevelDB GitHub](https://github.com/google/leveldb)

#### ex) MacOS에서의 설치 방법

```bash
$ brew install leveldb
```



### libsecp256k

ICON에서는 전자서명 생성 및 검증을 위해 secp256k 오픈소스를 사용한다. <br>ICON SCORE 개발 환경을 구축하기 위해서는 secp256k 개발 라이브러리의 사전 설치가 반드시 필요하다.<br>[secp256k GitHub](https://github.com/bitcoin-core/secp256k1)



#### ex) MacOS에서의 설치 방법

```bash

```

#### ex) Ubuntu Linux에서의 설치 방법

```bash
sudo apt-get install libsecp256k1-dev
```



### setup

```bash
# 작업 디렉토리 생성
$ mkdir work
$ cd work

# python 개발 환경 구축
$ virtualenv -p python3 .
$ source bin/activate

# ICON SCORE 개발 도구 설치
(work) $ pip install earlgrey-x.x.x-py3-none-any.whl
(work) $ pip install iconservice-x.x.x-py3-none-any.whl
(work) $ pip install tbears-x.x.x-py3-none-any.whl
```



## tbears 사용 방법

### configuration files



#### tbears configuration file

tbears의 작업 디렉토리 내 tbears.json 파일을 로딩한다.

**tbears.json**

```json
{
    "global": {
        "from": "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "port": 9000,
        "scoreRoot": "./.score",
        "dbRoot": "./.db",
        "genesisData": {
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
    },
    "log": {
        "colorLog": true,
        "level": "debug",
        "filePath": "./tbears.log",
        "outputType": "console|file"
    },
    "deploy": {
        "uri": "http://localhost:9000/api/v3",
        "stepLimit": "0x12345",
        "nonce": "0x123"
    }
}
```

**설명**

| 항목명           | 데이터 형식 | 설명                                                         |
| :--------------- | :---------- | :----------------------------------------------------------- |
| global           | dict        | tbears에서 전역적으로 사용하는 설정                          |
| global.from      | string      | tbears에서 JSON-RPC 서버로 메시지를 전송할 때 사용하는 from 주소 |
| global.port      | int         | JSON-RPC 서버의 포트 번호                                    |
| global.scoreRoot | string      | SCORE가 설치될 루트 디렉토리                                 |
| global.dbRoot    | string      | 상태 기록을 위한 DB 파일이 생성되는 루트 디렉토리            |
| global.accounts  | list        | 초기 코인을 가지고 있는 계좌 정보 목록<br>(index 0) genesis: 초기 코인을 가지고 있는 계좌 정보<br>(index 1) fee_treasury: transaction 처리 수수료를 수집하는 계좌 정보<br>(index 2~): 임의의 계좌 정보 |
| log              | dict        | tbears 로깅 설정                                             |
| log.level        | string      | 로그 메시지 표시 수준 정의<br/>"debug", "info", "warning", "error" |
| log.filePath     | string      | 로그 파일 경로                                               |
| log.outputType   | string      | “console”: tbears를 실행한 콘솔창에 로그 표시<br/>“file”: 지정된 파일 경로에 로그 기록<br/>“console\|file”: 콘솔과 파일에 동시 기록 |
| deploy           | dict        | SCORE 배포 시, 사용하는 설정                                 |
| deploy.uri       | string      | 요청을 보낼 uri                                              |
| deploy.stepLimit | string      | -(optional)                                                  |
| deploy.nonce     | string      | -(optional)                                                  |



#### score deploy configuration file

**deploy.json(tbears config 파일과 별도로 존재)**

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

**설명**

TODO: 설명 입력

| 항목명                  | 데이터 형식 | 설명                         |
| ----------------------- | :---------- | :--------------------------- |
| deploy                  | dict        | SCORE 배포 시, 사용하는 설정 |
| deploy.uri              | string      |                              |
| deploy.mode             | string      |                              |
| deploy.from             | string      |                              |
| deploy.to               | string      |                              |
| delploy.stepLimit       | string      |                              |
| scoreParams             | dict        |                              |
| scoreParams.init_supply | string      |                              |
| scoreParams.decimal     | string      |                              |



### Command-line interfaces(CLIs)



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

**directory**

TODO: tests 폴더 설명 입력

| **항목**                   | **설명**                                                     |
| :------------------------- | :----------------------------------------------------------- |
| \<project>                 | 이름의 SCORE 프로젝트 디렉토리 생성                          |
| tbears.json                | tbears의 기본 설정파일 생성                                  |
| \<project>/\_\_init\_\_.py | SCORE 프로젝트 디렉토리가 python 패키지 형식으로 인식되도록 한다. |
| \<project>/package.json    | SCORE의 메타 데이터                                          |
| \<project>/\<project>.py   | SCORE의 메인 파일. 내부에 ABCToken class가 정의되어 있다.    |
| tests                      |                                                              |



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
  -m {install,update}, --mode {install,update} eploy mode 
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





## 개발 지원 도구들

SCORE 개발하는데 도움이 되는 각종 유틸리티들에 대해 소개하고 사용 방법을 설명한다.

### Logger

콘솔 혹은 파일 형식으로 로그를 기록할 수 있는 기능을 제공하는 패키지

#### 함수 형식

```python
@staticmethod
def debug(msg: str, tag: str)
```

#### 사용 방법

```python
from iconservice.logger import Logger

TAG = 'ABCToken'

Logger.debug('debug log', TAG)
Logger.info('info log', TAG)
Logger.warning('warning log', TAG)
Logger.error('error log', TAG)
```

## ICON SCORE 개발 시 유의 사항

* tbears는 현 시점에서 loopchain 엔진을 포함하고 있지 않기 때문에 일부 SCORE 개발과 관련없는 JSON-RPC API 들은 동작하지 않을 수 있다.
    * tbears에서 지원하는 JSON-RPC API:
        * icx_getBalance, icx_getTotalSupply, icx_getBalance, icx_call, icx_sendTransaction, icx_getTransactionResult
* 이후 tbears 버전에서는 사용 방법이나 SCORE 개발 방법이 일부 변경될 수 있다.
* 개발의 편의성을 위해서 tbears에서 제공하는 JSON-RPC 서버는 transaction 내에 포함된  전자 서명을 검증하지 않는다.