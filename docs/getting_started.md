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


**Note** that you either have to have setuptools or distribute installed, the latter is preferred.
**Note**: If installing `Gevent` fails you probably need to install the `libevent`. On Ubuntu the package name for apt-get is `libevent-dev`.
If you don't want install Gevent, you can install with `--without-gevent` argument(`python setup.py install --without-gevent`)
 and start server with `--debug` argument, buildin Werkzeug will be used.
(`libcloud_rest --debug`).


## Run ##

After installing you will have libcloud_rest command.
Options:

    -h, --help         show help message and exit
    --host=HOST        Host to bind to
    --port=PORT        Port to listen on
    --log-level=LEVEL  Log level
    --log-file=PATH    Log file path. If not provided logs will go to stdout
    --debug            Enable debug mode, start serving without gevent with debug output

## Examples ##
[cURL](http://curl.haxx.se/) is a command line tool for transferring data with URL syntax.
It can be used to interact with the Libcloud REST API.


**Get list of images**  
You can request a image list  with this command in cURL:
```shell
curl libcloud-api:5000/0.1/compute/RACKSPACE_UK/images -H x-auth-user:user -H x-api-key:123
```
In return, you should get 200 OK response with list of images.
```json
[{"id": "31", "name": "Windows Server 2008 SP2 x86"},
 {"id": "85", "name": "Windows Server 2008 R2 x64"},
 {"id": "115", "name": "Ubuntu 11.04"},
 ...
]
```
**Create node**  
The call to create a server must use the POST method and request body must be JSON payload with node arguments.
```shell
curl -i -X POST localhost:5000/0.1/compute/RACKSPACE_UK/nodes -H x-auth-user:user -H x-api-key:123
-H  "Content-Type: application/json" -d '{"name": "rest_test","size_id" : "1", "image_id": "115"}'
```
Normal response would have stasus code 201 CREATED and looks like this:
```json
{"public_ips": ["0.0.0.0"],
 "state": 3,
 "id": "1",
 "name": "resttest"}
```
