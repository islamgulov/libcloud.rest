# REST API #
The REST API provide simple interface for most Libcloud functionality. All operations can be performed with standard HTTP calls. 

##Versions##
The API version is a part of the URL that is used to provide access to resources. API version is tied to a Libcloud version. So if you want to support multiple REST API versions you should for example use virtualenv and run Libcloud.REST instance per Libcloud version.  
All API call must use root URL in this format:

    <host>/<api version>
For example: 

	http://localhost:5000/0.1/

##REST API Resources##
The API provide interface for four libcloud components:  

 * [Compute](example.com)  
 * [Storage](example.com)  
 * [LoadBalancer](example.com)  
 * [DNS](example.com)

Each component have base API. Also some  provider have extension operations and some of base method can contain extra arguments.  
###List of supported providers###
All component have endpoint which returns list of support providers.  
List supported providers example:  

# REST API #
The REST API provide simple interface for most Libcloud functionality. All operations can be performed with standard HTTP calls. 

##Versions##
The API version is a part of the URL that is used to provide access to resources. API version is tied to a Libcloud version. So if you want to support multiple REST API versions you should for example use virtualenv and run Libcloud.REST instance per Libcloud version.  
All API call must use root URL in this format:

    <host>/<api version>
For example: 

	http://localhost:5000/0.1/

##REST API Resources##
The API provide interface for four libcloud components:  

 * [Compute](example.com)  
 * [Storage](example.com)  
 * [LoadBalancer](example.com)  
 * [DNS](example.com)

Each component have base API. Also some  provider have extension operations and some of base method can contain extra arguments.  
###List of supported providers###
`GET /<component>/providers/` - Returns list of component supported providers.

###Provider information###
`GET /<component>/providers/<provider id>` - Returns an array of provider specific operations information and required credentials. 

##Authentication##
Client have to sends provider specific credentials in X-headers with every request.
List of required X-headers described in provider information.

##Error Codes & Responses##
When there is an error, the header information contains:
 * Content-Type: application/json
 * HTTP status code

The body of the response constains elemements: 
 * code -  integer unique identifier for an error
 * name - error name
 * message - error message
 * detail - detailed error message

Sample of error response:
```http
HTTP/1.1 400 BAD REQUEST
Content-Length: 122
Content-Type: application/json

{
    "error": {
        "code": 1001, 
        "detail": "", 
        "message": "Provider UNKNOWN does not supported.", 
        "name": "ProviderNotSupported"
    }
}
```

The following table lists Libcloud.REST error codes:

| Error Code | Name | Message | HTTP Status Code |
|----------|----|-------|----------------|
|1000|UnknownError|An unknown error occurred.|500 Internal Server Error|
|1001|ProviderNotSupported|Provider `provider` does not supported.|400 Bad Request|
|1002|InternalError|We encountered an internal error.|500 Internal Server Error|
|1003|MissingHeaders|Your request was missing a required headers: `headers`.|400 Bad Request|
|1004|UnknownHeaders|Your request is containing a unknown headers: `headers`.|400 Bad Request|
|1005|InternalLibcloudError|We encountered an internal error in libcloud.|500 Internal Server Error|
|1006|ValidationError|An unknown error occurred.|400 Bad Request|
|1007|MalformedJSON|The JSON you provided is not well-formed.|400 Bad Request|
|1009|NoSuchZone|The specified zone does not exist|404 Not Found|
|1010|ZoneAlreadyExists|The requested zone already exists.|409 Conflict|
|1011|NoSuchRecord|The specified record does not exist|404 Not Found|
|1012|RecordAlreadyExists|The requested record already exists.|409 Conflict|
|1013|ArgumentsError|The request contain more than one of mutually exclusive arguments|400 Bad Request|
|1014|NoSuchContainer|The specified container does not exist|404 Not Found|
|1015|ContainerAlreadyExists|The requested container already exists.|409 Conflict|
|1016|InvalidContainerName|Invalid container name was provided|400 Bad Request|
|1017|ContainerIsNotEmpty|Container is not empty|400 Bad Request|
|1018|NoSuchObject|The specified Object does not exist|404 Not Found|





