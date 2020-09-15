#Zscaler Tools
Python Library used for interacting with Zscaler's public API

How to install:
```
pip install --index-url https://test.pypi.org/simple/ zscalertools
```

How to use:
```
import zscalertools
ztoolsinstance = zscalertools.api.zia('admin.zscalerbeta.net', 'test_api@user.com', 'password', 'Apikey')

ztoolsinstance.get_users()
```

Methods
  -------
  login()
    Attempts to create a web session to Zscaler API
  logout()
    Delete's existing web session to Zscaler API
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
  bulk_delete_users(ids=[])
    Bulk delete users up to a maximum of 500 users per request
  get_status()
    Gets the activation status for a configuration change
  activate_status()
    Activates configuration changes
  get_locations(search=None, sslScanEnabled=None, xffEnabled=None, authRequired=None, bwEnforced=None, page=None, pageSize=None)
    Gets information on locations
  get_location(id)
    Gets the location information for the specified ID
  add_location(location_object)
    Adds new locations and sub-locations
  get_locations_lite(includeSubLocations=None, includeParentLocations=None, sslScanEnabled=None, search=None, page=None, pageSize=None)
    Gets a name and ID dictionary of locations
  update_location(id, location_object)
    Updates the location and sub-location information for the specified ID
  pull_all_user_data()
    Pulls all users, departments and groups and returns 3 arrays