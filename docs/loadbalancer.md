##Load Balancer##
Load Balancer API allows you to manage Load Balancers as a service and services
such as Rackspace Cloud Load Balancers, GoGrid Load Balancers
and Ninefold Load Balancers.

###Resources###

| Resource| Description|
|---------|------------|
GET `/loadbalancer/providers` | Returns a list of supported providers
GET `/loadbalancer/providers/<provider>` | Returns a list of supported methods for this provider.
GET `/loadbalancer/<provider>/balancers` | Returns a list of the available LoadBalancer instances
POST `/loadbalancer<provider>/balancers` | Create a new load balancer
PUT `/loadbalancer/<provider>/balancers/<balancer id>` | Update load balancer
DELETE `/loadbalancer/<provider>/balancers/<balancer id>` | Delete load balancer
GET `/loadbalancer/<provider>/balancers/<balancer id>` | Returns a loadBalancer details
GET `/loadbalancer/<provider>/balancers/<balancer id>/members` | Returns a list of members
POST `/loadbalancer/<provider>/balancers/<balancer id>/members` |  Add a new member to the load balancer
DELETE `/loadbalancer/<provider>/balancers/<balancer id>/members/<member id>` |  Remove a member from the load balancer
GET `/loadbalancer/<provider>/protocols` | Returns a list Load Balancing Protocols
GET `/loadbalancer/<provider>/algorithms` | Returns a list Load Balancing Algorithms

