##Storage##
Storage API allows you to manage cloud storage and services such as Amazon S3,
 Rackspace CloudFiles, Google Storage and others.

###Resources###

| Resource| Description|
|---------|------------|
|GET `/storage/providers` | Returns list of supported providers|
|GET `/storage/<provider>/containers/` | Returns list of containers|
|GET `/storage/<provider>/containers/<container>/` | Returns container details|
|POST` /storage/<provider>/containers/<container>` | Create container|
|DELETE `/storage/<provider>/containers/<container>` | Delete container|
|GET `/storage/<provider>/containers/<container>/objects/`| Returns list objects|
|GET `/<storage>/<provider>/containers/<container>/objects/<object>/metadata` | Return object infromation|
|GET `/<storage>/<provider>/containers/ <container>/objects/<object>` | Download object. The object's data is returned in the response body.|
|POST `/<storage>/<provider>/containers/<container>/objects`| Upload object. Conternt type for an object must be included in HTTP headers to the request and the data payload in the request body.|
|DELETE `/<storage>/<provider>/containers/ <container>/objects/<object>` | Delete object|

