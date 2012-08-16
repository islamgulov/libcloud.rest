##Compute##
Compute component allows you to manage cloud and virtual
servers offered by different providers such as Amazon, Rackspace,
Linode and more than 20 others.

###Resources###

| Resource| Description|
|---------|------------|
|GET `/compute/providers` | Returns list of supported providers|
|GET `/compute/providers/<provider>`| Returns provider detailed information|
|GET `/compute/<provider>/nodes`| Returns list of nodes|
|GET `/compute/<provider>/sizes`| Returns list of available node sizes|
|GET `/compute/<provider>/images`| Returns list of available node images|
|GET `/compute/<provider>/locations`| Returns list of data centers|
|POST `/compute/<provider>/nodes`| Returns create new node|
|POST `/compute/<provider>/nodes/<node id>/reboot`| Reboot a node|
|DELETE `/compute/<provider>/nodes/<node id>`| Delete (destroy) a node|
|POST `/compute/<method name>`| Invoke provider specific method|





