#!/usr/bin/env python

import time
import datetime
import re
import json
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, HTTPError

import logging

zapi_adapter = HTTPAdapter(max_retries=3)

logger = logging.getLogger(__name__)

class zia:
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
    
    return "{}&{}={}".format(current_path, attribute, value)
  
  def _handle_response(self, response):
    try:
      if response.ok:
        return response.json()
      else:
        response.raise_for_status()
    except HTTPError as e:
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

  def get_user(self, id):
    api_path = '/users/{}'.format(id)

    return self._handle_response(self.session.get(self._url(api_path)))
  
  def get_groups(self, search=None, page=None, pageSize=None):
    logger.debug("get_groups module called")
    api_path = '/groups'
    
    return self._handle_response(self.session.get(self._url(api_path)))

  def get_group(self, id):
    api_path = '/group/{}'.format(id)

    return self._handle_response(self.session.get(self._url(api_path)))

  def get_departments(self, name=None, page=None, pageSize=None):
    logger.debug("get_departments module called")
    api_path = '/departments?'
    if pageSize:
      api_path = api_path + "pageSize={}".format(pageSize)
    
    return self._handle_response(self.session.get(self._url(api_path)))
  
  def get_department(self, id):
    api_path = '/departments/{}'.format(id)

    return self._handle_response(self.session.get(self._url(api_path)))
  
  def add_user(self, user_object):
    api_path = '/users/'
    data = json.dumps(user_object)
    
    return self._handle_response(self.session.post(self._url(api_path), data=data))
  
  def update_user(self, id, user_object):
    api_path = '/users/{}'.format(id)
    data = json.dumps(user_object)

    return self._handle_response(self.session.put(self._url(api_path), data=data))

  def bulk_delete_users(self, ids=[]):
    api_path = '/users/bulkDelete'
    body = {}
    body['ids'] = ids
    data = json.dumps(body)
    
    return self._handle_response(self.session.post(self._url(api_path), data=data))

  def get_status(self):
    api_path = '/status'
    
    return self._handle_response(self.session.get(self._url(api_path)))
  
  def activate_status(self):
    api_path = '/status/activate'

    return self._handle_response(self.session.post(self._url(api_path)))
  
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
    
  def get_location(self, id):
    api_path = '/locations/{}'.format(id)

    return self._handle_response(self.session.get(self._url(api_path)))
  
  def add_location(self, location_object):
    api_path = '/locations'
    data = json.dumps(location_object)
    
    return self._handle_response(self.session.post(self._url(api_path), data=data))
  
  def get_locations_lite(self, includeSubLocations=None, includeParentLocations=None, sslScanEnabled=None, search=None, page=None, pageSize=None):
    api_path = "/locations/lite" 
    
    return self._handle_response(self.session.get(self._url(api_path)))
  
  def update_location(self, id, location_object):
    api_path = '/locations/{}'.format(id)
    data = json.dumps(location_object)

    return self._handle_response(self.session.put(self._url(api_path), data=data))

class helper():
  """
  Class for ZIA to help with function calls
  """
  
  def __init__(self, api_object):
    logger.debug('calling init method called for helper class')
    try:
      if isinstance(api_object, zia):
        logger.error("YAYYYA ITS RIGHT")
        self.api = api_object
      else:
        raise
    except:
      raise
      
  
  def pull_all_zia_data(self):
      logger.info("Zscaler Helper -  Pulling All User/Group Data")
      zscaler_users = self.api.get_users(pageSize=200000)
      zscaler_departments = self.api.get_departments(pageSize=10000)
      zscaler_groups = self.api.get_groups()
      logger.info("Zscaler API - Data Pull Complete")
      return zscaler_users, zscaler_departments, zscaler_groups