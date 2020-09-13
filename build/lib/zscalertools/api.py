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

class exception(Exception):
  pass

class zia:
  """Zscaler Internet Security API Library"""

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
    api_path = '/users'
    query = '?'
    if group:
      api_path = api_path + "{}group={}".format(query, group)
      query = '&'
    if pageSize:
      api_path = api_path + "{}pageSize={}".format(query, pageSize)

    return self._handle_response(self.session.get(self._url(api_path)))

  def get_groups(self, search=None, page=None, pageSize=None):
    logger.debug("get_groups module called")
    api_path = '/groups'
    
    return self._handle_response(self.session.get(self._url(api_path)))

  def get_departments(self, name=None, page=None, pageSize=None):
    logger.debug("get_departments module called")
    api_path = '/departments?'
    if pageSize:
      api_path = api_path + "pageSize={}".format(pageSize)
    
    return self._handle_response(self.session.get(self._url(api_path)))
  
  def get_user(self, id):
    api_path = '/users/{}'.format(id)

    return self._handle_response(self.session.get(self._url(api_path)))
  
  def add_user(self, details):
    api_path = '/users/'
    data = json.dumps(details)
    
    return self._handle_response(self.session.post(self._url(api_path), data=data))
  
  def update_user(self, id, details):
    api_path = '/users/{}'.format(id)
    data = json.dumps(details)

    return self._handle_response(self.session.put(self._url(api_path), data=data))

  def get_users(self, name=None, dept=None, group=None, page=None, pageSize=None):
    api_path = '/users'
    query = '?'
    if group:
      api_path = api_path + "{}group={}".format(query, group)
      query = '&'
    if pageSize:
      api_path = api_path + "{}pageSize={}".format(query, pageSize)

    return self._handle_response(self.session.get(self._url(api_path)))

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