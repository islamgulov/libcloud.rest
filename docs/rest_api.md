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
Error responses structure:

 * code -  integer unique identifier for an error
 * name - error name
 * message - error message
 * detail - detailed error message

[List of error codes](example.com) 




