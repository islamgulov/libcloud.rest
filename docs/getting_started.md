#Getting started#

## Requirements ##
* Python 2.x>=2.5
* Apache Libcloud
* Werkzeug
* Gevent

## Supported Python Versions ##
* Python from 2.5 up to 2.7
* PyPy

## Installation##

### Using git##
**System-Wide installation** 
 
	$ git clone 	https://github.com/islamgulov/libcloud.rest  
	$ cd libcloud.rest
	$ python setup.py install`  


**Note**: If installing `Gevent` fails you probably need to install the `libevent`. On Ubuntu the package name for apt-get is `libevent-dev`.


## Run ##

After installing you will have libcloud_rest command.  
Options:

    -h, --help         show help message and exit
    --host=HOST        Host to bind to  
    --port=PORT        Port to listen on
    --log-level=LEVEL  Log level
    --log-file=PATH    Log file path. If not provided logs will go to stdout
    --debug            Enable debug mode