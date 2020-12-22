# Zscaler Tools
Python Library used for interacting with Zscaler's public API

## General Information
This Python Library is being devloped to provide an easily usable interface with Zscaler API.  
> https://help.zscaler.com/zia/api

Zscaler API Functions in this Library
- ZIA
  - [x] Activation
  - [ ] Admin Audit Logs
  - [ ] Admin & Role Management
  - [x] API Authentication
  - [ ] Cloud Sandbox Report
  - [ ] Firewall Policies
  - [x] Location Management
  - [ ] Security Policy Settings
  - [ ] SSL Inspection Settings
  - [ ] Traffic Forwarding
  - [x] User Management
  - [ ] URL Categories
  - [ ] URL Filtering Policies
  - [ ] User Authentication Settings
- ZPA
  - API not released by Zscaler

## Features
- Manage Request Sessions to Zscaler API
  - You do not need to explicitly call the login() function
- Manage Auto-Retry (3 retries per call)
- Manage 429 API Rate Limit Reponse
  - Library will read response and wait for Rate Limit before continuing

## How to install:
```
pip install zscalertools
```

## How to use:
```
import zscalertools
ztools_zia_api = zscalertools.zia('admin.zscalerbeta.net', 'test_api@user.com', 'password', 'Apikey')

ztools_zia_api.get_users()
```

  
  Attributes
  ----------
  ```
  cloud : str
    a string containing the zscaler cloud to use
  username : str
    the username of the account to connect to the zscaler cloud
  password : str
    the password for the username string
  apikey : str
    apikey needed to connect to zscaler cloud
  ```
  Zscaler Methods
  ---------------

    API Authentication
    ------------------
    login()
      Attempts to create a web session to Zscaler API
    logout()
      Delete's existing web session to Zscaler API
    
    Activation
    ----------
    get_status()
      Gets the activation status for a configuration change
    activate_status()
      Activates configuration changes

    User Management
    ---------------
    get_users(name=None, dept=None, group=None, page=None, pageSize=None)
      Gets a list of all users and allows user filtering by name, department, or group
    get_user(id)
      Gets the user information for the specified ID
    get_groups(search=None, page=None, pageSize=None)
      Gets a list of groups
    get_group(id)
      Gets the group for the specified ID
    get_departments(search=None, name=None, page=None, pageSize=None)
      Gets a list of departments
    get_department(id)
      Gets the department for the specified ID
    add_user(user_object)
      Adds a new user
    update_user(id, user_object)
      Updates the user information for the specified ID
    delete_user(id)
      Deletes the user for the specified ID
    bulk_delete_users(ids=[])
      Bulk delete users up to a maximum of 500 users per request
    
    Location Management
    -------------------
    get_locations(search=None, sslScanEnabled=None, xffEnabled=None, authRequired=None, bwEnforced=None, page=None, pageSize=None)
      Gets information on locations
    get_location(id)
      Gets the location information for the specified ID
    get_sublocations(id, search=None, sslScanEnabled=None, xffEnabled=None, authRequired=None, bwEnforced=None, page=None, pageSize=None, enforceAup=None, enableFirewall=None)
      Gets the sub-location information for the location with the specified ID. These are the sub-locations associated to the parent location
    add_location(location_object)
      Adds new locations and sub-locations
    get_locations_lite(includeSubLocations=None, includeParentLocations=None, sslScanEnabled=None, search=None, page=None, pageSize=None)
      Gets a name and ID dictionary of locations
    update_location(id, location_object)
      Updates the location and sub-location information for the specified ID
    delete_location(id)
      Deletes the location or sub-location for the specified ID
    buld_delete_locations(ids=[])
      Bulk delete locations up to a maximum of 100 users per request. The response returns the location IDs that were successfully deleted.

  Custom Methods
  --------------
  ```
  pull_all_user_data()
    Pulls all users, departments and groups and returns 3 arrays (up to 999,999 entries a piece)
  ```

## Contributing
Pull requests are welcome.  Initial development is focused on building out the rest of the library.

Please make sure to update tests as appropriate.