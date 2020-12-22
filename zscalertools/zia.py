#!/usr/bin/env python

import time
import datetime
import re
import json
import requests
from functools import wraps
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, HTTPError

import logging

zapi_adapter = HTTPAdapter(max_retries=3)

logger = logging.getLogger(__name__)

class ZiaThrottleException(Exception):
  def __init__(self, text):
    self.text = text

class ZiaSessionException(Exception):
  def __init__(self, text):
    self.text = text

def retry(exceptions, tries=4, delay=3, backoff=2):
  """
  Retry calling the decorated function using an exponential backoff.

  Args:
      exceptions: The exception to check. may be a tuple of
          exceptions to check.
      tries: Number of times to try (not retry) before giving up.
      delay: Initial delay between retries in seconds.
      backoff: Backoff multiplier (e.g. value of 2 will double the delay
          each retry).
  """
  def deco_retry(f):
    @wraps(f)
    def f_retry(*args, **kwargs):
      mtries, mdelay = tries, delay
      while mtries > 1:
        try:
          return f(*args, **kwargs)
        except ZiaThrottleException as e:
          retry_after = int(json.loads(e.text)['Retry-After'][0]) + 1
          logger.info("{}, Retrying in {} seconds...".format(e, retry_after))
          time.sleep(retry_after)
          mtries -= 1
        except ZiaSessionException as e:
          logger.error("Error Received - {}.  Need to re-generate session".format(e))
        except exceptions as e:
          logger.info("{}, Retrying in {} seconds...".format(e, mdelay))
          time.sleep(mdelay)
          mtries -= 1
          mdelay *= backoff
      return f(*args, **kwargs)
    return f_retry  # true decorator
  return deco_retry
 
class api:
  """
  Class to represent Zscaler Internet Security Instance
  
  Attributes
  ----------
  cloud : str
    a string containing the zscaler cloud to use
  username : str
    the username of the account to connect to the zscaler cloud
  password : str
    the password for the username string
  apikey : str
    apikey needed to connect to zscaler cloud
    
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
    bulk_delete_users(ids=[])
      Bulk delete users up to a maximum of 500 users per request
    
    
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
  
  Custom Methods
  -------
  pull_all_user_data()
    Pulls all users, departments and groups and returns 3 arrays
  """

  def __init__(self, cloud, username, password, apikey):

    logger.debug('Calling Init method called for zia class')
    self.url = "https://{}/api/v1".format(cloud)
    self.username = username
    self.password = password
    self.apikey = apikey
    
    zapi_adapter = HTTPAdapter(max_retries=3)
    self.session = requests.Session()
    self.session.mount(self.url, zapi_adapter)


    self.jsessionid = None

  def obfuscateApiKey (self):
    seed = self.apikey
    now = int(time.time() * 1000)
    n = str(now)[-6:]
    r = str(int(n) >> 1).zfill(6)
    key = ""
    for i in range(0, len(str(n)), 1):
      key += seed[int(str(n)[i])]
    for j in range(0, len(str(r)), 1):
      key += seed[int(str(r)[j])+2]

    return now, key

  def _url(self, path):

    return self.url + path
  
  def _append_url_query(self, current_path, attribute, value):
    if current_path.endswith('?'):
      return "{}{}={}".format(current_path, attribute, value)
    else:
      return "{}&{}={}".format(current_path, attribute, value)

  def _handle_response(self, response):
    try:
      if response.ok:
        return response.json()
      else:
        response.raise_for_status()
    except HTTPError as e:
      if response.status_code == 429:
        raise ZiaThrottleException(response.text)
      elif response.status_code == 401:
        self.login()
        raise ZiaSessionException(response.text)
      else:
        logger.error("Response - {} - {}".format(response.status_code, response.text))
        raise
    
  def login(self):
    logger.debug("login module called")
    api_path = '/authenticatedSession'
    timestamp, obf_key = self.obfuscateApiKey()
    self.session.headers.update({ 'Content-Type' :  'application/json',
                                  'cache-control': 'no-cache'})
    body = {
      'apiKey': obf_key,
      'username': self.username,
      'password': self.password,
      'timestamp': timestamp,
    }
    data = json.dumps(body)

    return self._handle_response(self.session.post(self._url(api_path), data=data))
  
  def logout(self):
    logger.debug("logout module called")
    api_path = '/authenticatedSession'

    return self._handle_response(self.session.delete(self._url(api_path)))
  
  @retry(Exception, tries=3)
  def get_users(self, name=None, dept=None, group=None, page=None, pageSize=None):
    api_path = '/users?'
    if name:
      api_path = self._append_url_query(api_path, 'name', name)
    if dept:
      api_path = self._append_url_query(api_path, 'dept', dept)
    if group:
      api_path = self._append_url_query(api_path, 'page', page)
    if pageSize:
      api_path = self._append_url_query(api_path, 'pageSize', pageSize)

    return self._handle_response(self.session.get(self._url(api_path)))
    #return self.session.get(self._url(api_path))

  @retry(Exception, tries=3)
  def get_user(self, id):
    api_path = '/users/{}'.format(id)

    return self._handle_response(self.session.get(self._url(api_path)))
  
  @retry(Exception, tries=3)
  def get_groups(self, search=None, page=None, pageSize=None):
    logger.debug("get_groups module called")
    api_path = '/groups'
    
    return self._handle_response(self.session.get(self._url(api_path)))

  @retry(Exception, tries=3)
  def get_group(self, id):
    api_path = '/group/{}'.format(id)

    return self._handle_response(self.session.get(self._url(api_path)))

  @retry(Exception, tries=3)
  def get_departments(self, name=None, page=None, pageSize=None):
    logger.debug("get_departments module called")
    api_path = '/departments?'
    if pageSize:
      api_path = api_path + "pageSize={}".format(pageSize)
    
    return self._handle_response(self.session.get(self._url(api_path)))
  
  @retry(Exception, tries=3)
  def get_department(self, id):
    api_path = '/departments/{}'.format(id)

    return self._handle_response(self.session.get(self._url(api_path)))
  
  @retry(Exception, tries=3)
  def add_user(self, user_object):
    api_path = '/users/'
    data = json.dumps(user_object)
    
    return self._handle_response(self.session.post(self._url(api_path), data=data))
  
  @retry(Exception, tries=3)
  def update_user(self, id, user_object):
    api_path = '/users/{}'.format(id)
    data = json.dumps(user_object)

    return self._handle_response(self.session.put(self._url(api_path), data=data))

  @retry(Exception, tries=3)
  def bulk_delete_users(self, ids=[]):
    api_path = '/users/bulkDelete'
    body = {}
    body['ids'] = ids
    data = json.dumps(body)
    
    return self._handle_response(self.session.post(self._url(api_path), data=data))

  @retry(Exception, tries=3)
  def get_status(self):
    api_path = '/status'
    
    return self._handle_response(self.session.get(self._url(api_path)))
  
  @retry(Exception, tries=3)
  def activate_status(self):
    api_path = '/status/activate'

    return self._handle_response(self.session.post(self._url(api_path)))
  
  @retry(Exception, tries=3)
  def get_locations(self, search=None, sslScanEnabled=None, xffEnabled=None, authRequired=None, bwEnforced=None, page=None, pageSize=None):
    api_path = '/locations?'
    
    if search:
      api_path = self._append_url_query(api_path, 'search', search)
    if sslScanEnabled:
      api_path = self._append_url_query(api_path, 'sslScanEnabled', sslScanEnabled)
    if xffEnabled:
      api_path = self._append_url_query(api_path, 'xffEnabled', xffEnabled)
    if authRequired:
      api_path = self._append_url_query(api_path, 'authRequired', authRequired)
    if bwEnforced:
      api_path = self._append_url_query(api_path, 'bwEnforced', bwEnforced)
    if page:
      api_path = self._append_url_query(api_path, 'page', page)
    if pageSize:
      api_path = self._append_url_query(api_path, 'pageSize', pageSize)

    return self._handle_response(self.session.get(self._url(api_path)))
  
  @retry(Exception, tries=3)
  def get_location(self, id):
    api_path = '/locations/{}'.format(id)

    return self._handle_response(self.session.get(self._url(api_path)))
  
  @retry(Exception, tries=3)
  def add_location(self, location_object):
    api_path = '/locations'
    data = json.dumps(location_object)
    
    return self._handle_response(self.session.post(self._url(api_path), data=data))
  
  @retry(Exception, tries=3)
  def get_locations_lite(self, includeSubLocations=None, includeParentLocations=None, sslScanEnabled=None, search=None, page=None, pageSize=None):
    api_path = "/locations/lite" 
    
    return self._handle_response(self.session.get(self._url(api_path)))
  
  @retry(Exception, tries=3)
  def update_location(self, id, location_object):
    api_path = '/locations/{}'.format(id)
    data = json.dumps(location_object)

    return self._handle_response(self.session.put(self._url(api_path), data=data))
  
  def pull_all_user_data(self):
    logger.info("Zscaler Helper -  Pulling All User/Group Data")
    zscaler_users = self.get_users(pageSize=999999)
    zscaler_departments = self.get_departments(pageSize=999999)
    zscaler_groups = self.get_groups(pageSize=999999)
    print("Users - {}, Deparments - {}, Groups - {}".format(len(zscaler_users), len(zscaler_departments), len(zscaler_groups)))
    logger.info("Zscaler API - Data Pull Complete")
    return zscaler_users, zscaler_departments, zscaler_groups