# libcloud.rest [![Build Status](https://secure.travis-ci.org/islamgulov/libcloud.rest.png)](http://travis-ci.org/islamgulov/libcloud.rest)

REST interface for [Libcloud][1] which exposes all the Libcloud functionality
through a RESTful API. Currently Libcloud has a big limitation - you can only
use it with Python. REST interface allows users to leverage Libcloud 
functionality through an arbitrary language which knows how to talk HTTP.

Note: This is an Apache Google Summer of Code 2012 project.

## Deploying

By default Libcloud REST runs using gevent's WSGI handler. Gevent WSGI handler
doesn't support SSL which means that if you want to use SSL you need to use a
some kind of SSL terminator such as [stud][4].

# Links

* [Strategic plan][2]
* [GSoC Proposal][3]

[1]: http://libcloud.apache.org
[2]: https://docs.google.com/document/d/1P9fIxILn-WdgpkXDPydHB_dghGs-BYuoSmkFwh0Y36w/edit
[3]: http://www.google-melange.com/gsoc/project/google/gsoc2012/islamgulov/11001
[4]: https://github.com/bumptech/stud.git
