# ChangeLog - T-Bears

## 1.8.0 - 2021-02-25
* Update `sync_mainnet` command
    * add revision 12

## 1.7.2 - 2020-10-22
* Update `sync_mainnet` command
    * add revision 10, 11
* Fix SCORE unittest Framework (#81)

## 1.7.1 - 2020-08-10
* Fix `sync_mainnet` command
    * Fix invalid governance SCORE 1.1.1

## 1.7.0 - 2020-07-07
* Add `sync_mainnet` command
    * sync revision and governance SCORE with the mainnet
    * makes 4 main P-Reps to make decentralized network
* Substitute `coincurve` for `secp256k1`
* `genconf` command makes keystore files for 4 main P-Reps

## 1.6.4 - 2020-06-05
* Fix deploy command (#70)

## 1.6.3 - 2020-06-02
* Fix SCORE unittest framework (#69)

## 1.6.2 - 2020-05-29
* Fix SCORE unittest framework (#68)
    * owner property bug
    * patch deprecated SCORE methods to warning
* Fix minor bugs
    * error code for get_tx_info message with invalid TX hash
    * prevVotes list management
    * write_precommit_state message parameter

## 1.6.1 - 2020-05-20
* Add --nid option to 'sendtx' command (#66)

## 1.6.0 - 2020-04-08
* Support block version 0.3 and above (#59)
* Apply iconsdk (#54)
* Add 'keyinfo' command (#56)
* Fix 'sendtx' command bug (#61)

## 1.5.0 - 2019-09-02
* Support IISS

## 1.4.0 - 2019-08-19
* Add 'keyinfo' command to query keyinfo file content
* Fix the bug of 'transfer' command transfering invalid amount of ICX

## 1.3.0 - 2019-07-16
* Update Docker image files for Fee 2.0

## 1.2.2 - 2019-06-21
* Add the transaction signature verifier
* Fix the bug of generating invalid signature after estimating Step

## 1.2.1 - 2019-06-12
* Add `stepLimit` estimate logic to `deploy`, `sendtx`, and `transfer` commands
* Apply block hash compatibility to test module

## 1.2.0 - 2019-05-22
* Improve Docker image generation
* Refactor sub processes management
* Migrate `package.json` format
* Add SCORE unittest framework

## 1.1.0.1 - 2019-01-03
* Fix wrong description of blockConfirmInterval in README.md
* Fix block query error

## 1.1.0 - 2018-11-29
* Add test command
* Add SCORE integration test library
* Add -v, --verbose option
* Modify init command to generate test code
* Deprecate samples command

## 1.0.6.2 - 2018-10-19
* Fix configuration file loading bug
* Modify python version requirements to 3.6.5+

## 1.0.6.1 - 2018-10-16
* Fix deploy command bug

## 1.0.6 - 2018-10-12
* Add '--step-limit' option to the 'deploy' and 'transfer' commands
* Support docker image - iconloop/tbears
* Fix minor bugs

## 1.0.5.1 - 2018-09-07
* Remove sanic package from dependencies

## 1.0.5 - 2018-09-06
* '-t' option of the deploy command deprecated. Deploy command supports zip type only.
* Remove runtime warning message of T-Bears block_manager.
* Modify the deploy command. Deploy command can get directory and zip file as a project.
* Fix the transfer command to read 'stepLimit' from the configuration file.
* Add test account 'test1' in genesis block.
* Modify the keystore command to receive the password twice to confirm it.

## 1.0.4 - 2018-08-28
* Change the encryption parameter 'N' of keystore
* Improve IconClient error handling
* Update README.md

## 1.0.3 - 2018-08-24
* Add interactive mode. Activate with 'console' command
* Add '-p' option to 'deploy' command. Now can enter keystore file password as argument.
* Add block manager. 
* Rename tbears_tutorial.md to README.md

## 1.0.0 - 2018-08-15
* Tbears service support 'call', 'sendtx' and 'genconf' command
    * call : Send icx_call request
    * sendtx : Send icx_sendTransaction request
    * genconf : Generate tbears configuration files. (tbears_server_config.json, tbears_cli_config.json)

## 0.9.8 - 2018-08-09
* Tbears service support 'lastblock', 'blockbyhash' and 'blockbyheight' command
    * Can query block information on tbears service now
* Proofread tbears_tutorial.md

## 0.9.7 - 2018-08-03
* Fix the bug that '-a' option of start command does not work
* Exception logs are saved separately

## 0.9.6.1 - 2018-07-31

* Fix configuration file loading bug
* Add commands (lastblock, blockbyhash, blockbyheight)
    * update tbears_tutorial.md
   
## 0.9.6 - 2018-07-27

* Support log rotation with ICON Commons
* Add commands (balance, totalsupply, scoreapi)
    * tbears_tutorial.md is out of date. It will be updated later

## 0.9.5.1 - 2018-07-24

* Improve configuration files
    * check 'Configuration Files' chapter of tbears_tutorial.md

## 0.9.5 - 2018-07-20

* Use ICON common package for configuration file and logging module
* Improve the output message of deploy command
    * Success response : print transaction hash in response
    * Error response : print response message
* Add command
    * txresult : Get transaction result by transaction hash
    * transfer: Transfer ICX coin
* Add network ID
    *  Check icx_sendTransaction method parameter 'nid' of tbears JSON-RPC API document
    * 'Add -n', '--nid' option on deploy command.
