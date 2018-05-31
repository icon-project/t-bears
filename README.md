tbears (T-bears)
=======

```tbears``` is the utility tool to help SCORE(Smart Contract On Reliable Environment)development.

## Getting Started
You need to install wheel file of tbears and iconservice by using PIP.

### Prerequisites
* macOS / Linux (Ubuntu 16.04, or Centos)
	* Need to test depply on Windows 10
* Over Docker CE 18.03.x
* Python 3.6 and above

### Installation

At First, if you are on macOS, you have to install leveldb library.
 ```
 $ brew install leveldb    # Install leveldb on MacOS.
 ```

Then pip install wheel files of tbears and iconservice in Wiki.


### Create SCORE project
 ```tbears``` create the basic ```package.json``` and python code.
```
$ tbears init <project> <class>
```
 If you named your SCORE project as ```foo``` and SCORE class as ```Foo```, then ```tbears``` will create project like below.

 ```
 -foo
  +--__init__.py
  |
  +--foo.py
  |
  +--package.json
 ```
  The meaning of each file is
  * ```package.json``` : SCORE package information file. ```loopchain ``` will access this file when it loads the SCORE.
  * ```foo.py``` : Python source code to implement SCORE.

### Run SCORE project

 Run the SCORE project by the ```tbears ```. It will launch SCORE process and keep running until user stops the process by pressing [Ctrl+c]. ```tbears``` runs unit test first and launch SCORE process because not to skip the basic TDD priciple.
```
$ tbears run <project>
```

### Stop SCORE project

 Stop the SCORE project by the ```tbears ```. It will stop SCORE process.
```
$ tbears stop
```

### Clear SCORE project

 Clear the SCORE project by the ```tbears ```. It will remove both .score and .db directory.
```
$ tbears clear
```

### Reference
* [SCORE development guide and examples](https://repo.theloop.co.kr/icon/loopchain-icon/blob/master/icon/docs/dapp_guide.md)
* [Architecture of IconService](https://repo.theloop.co.kr/icon/loopchain-icon/blob/master/icon/docs/class.md)

### Deploy SCORE project into the test net or main net

To-Do

## Contributing

To-Do

## Versioning

 v0.9.0

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments
 To-Do
