tbears (T-bears)
=======

```tbears``` is the utility tool to help SCORE(Smart Contract On Reliable Environment)development.

## Getting Started
You need to install tbears by using PIP.

### Prerequisites
* macOS / Linux (Ubuntu 16.04, or Centos)
	* Need to test depply on Windows 10
* Over Docker CE 18.03.x
* Python 3.6 and above

### Installation

Most simplest way is using PIP.

```
pip install tbears
```

And you can see the following message if you type ```tbears ``` in the console.

```
$ tbears --version
tbears version 0.0.1
```

### Create SCORE project
 ```tbears``` create the basic ```package.json``` and python code.
```
$ tbears init <project>
```
 If you named your project as ```foo```, then ```tbears``` will create project like below.

 ```
 -foo
  +--package.json
  |
  +--foo.py
 ```
  The meaning of each file is
  * ```package.json``` : SCORE package informatino file. ```loopchain ``` will access this file when it loads the SCORE.
  * ```foo.py``` : Python source code to implement SCORE.

### Run SCORE project

 Run the SCORE project by the ```tbears ```. It will launch SCORE process and keep running until user stops the process by pressing [Ctrl+c]. ```tbears``` runs unit test first and launch SCORE process because not to skip the basic TDD priciple.

```
$ tbears run <project>

 Run unit test of <project>......
 Finished to run unit test.

 Running SCORE.... press [Ctrl+c] if you stop the SCORE process.
```


### Implement SCORE
 Read the [SCORE development guide]().


### Deploy SCORE project into the test net or main net

To-Do


## Development

 At First, clone this project. Then go to the project folder and create user environment. This is how to create the user environment.
 ```
 $ virtualenv -p python3 .    # Create the virtual environment.
 $ source bin/activate    # Enter the virtual environment.
 $ pip install -r requirements.txt    # Install necessary packages in the virtual environment.
 ```
 If you are on macOS, you have to install leveldb library.
 ```
 $ brew install leveldb    # Install leveldb on MacOS.
 ```

## Running the unit test
After installation, execute the whole unit test like the following in order to check whether it operates well.

```
$ python setup.py test
```

## Contributing

To-Do:

## Versioning

 v0.0.1

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments
 To-Do
