##DNS##
DNS API allows you to manage DNS as A Service and services such as Zerigo DNS,
Rackspace Cloud DNS and others.

###Resources###

| Resource| Description|
|---------|------------|
GET `/dns/providers` | Returns a list of supported providers
GET `/dns/providers/<provider>` | Returns a list of supported methods for this provider.
GET `/dns/<provider>/zones` | List of the zone objects
GET `/dns/<provider>/zones/<zone id>` | Zone details
POST `/dns/<provider>/zones` |Create a new zone
PUT `/dns/<provider>/zones/<zone id>` | Update zone
DELETE `/dns/<provider>/zones/<zone id>` | Delete zone
GET `/dns/<provider>/zones/<zone id>/records` | List of Record objects for the specified zone
GET `/dns/<provider>/zones/<zone id>/records/<record id>` | Record details
POST `/dns/<provider>/zones/<zone id>/records/` | Create record
PUT `/dns/<provider>/zones/<zone id>/records/<record id>` | Update record
DELETE `/dns/<provider>/zones/<zone id>/records/<record id>` | Delete record
GET `/dns/<provider>/zones/<id>/records/types` | Returns list of record types

