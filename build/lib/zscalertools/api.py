#!/usr/bin/env python

import time
import datetime
import re
import json
import requests
import logging

logger = logging.getLogger(__name__)

class zia:
  """Zscaler Internet Security API Library"""

  def __init__(self, cloud, username, password, apikey):

    logger.debug('Init method called for zia class')
    self.url = "https://{}/api/v1".format(cloud)
    self.username = username
    self.password = password
    self.apikey = apikey

    self.authenticatetime = None
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

  def authenticate(self):
    logger.debug("authenticate module called")
    if self.jsessionid == None:
      logger.debug("No JSESSIONID Found")
      self.login()
    else:
      api_path = '/authenticatedSession'
      headers = {'Content-Type' :  'application/json',
                 'cache-control': 'no-cache',
                 'cookie' : self.jsessionid}
      method = 'GET'

      try:
        request = self._api_call(api_path, method, headers=headers)
        if request.status_code == 200:
          response_data = request.json()
          self.logger.debug('login token confirmed')
          return response_data
        else:
          error = "{} - {}".format(request.status_code, request.text)
          self.login()
      except Exception as e:
        logger.debug("Receieved error - {} - attempting to re-login".format(e))

  def logout(self):
    logger.debug("logout module called")
    api_path = '/authenticatedSession'
    headers = {'Content-Type' :  'application/json',
               'cache-control': 'no-cache',
               'cookie' : self.jsessionid}
    method = 'DELETE'

    try:
      request = self._api_call(api_path, method, headers=headers)
    except requests.exceptions.HTTPError as e:
      logger.info("Logout attempted - but no valid session found - {}".format(e))
    except Exception as e:
      logger.error("Failed to Logout of API")
      return False
    else:
      logger.debug("Logout Module Successful")
      return request.json()

  def login(self):
    logger.debug("login module called")
    api_path = '/authenticatedSession'
    timestamp, obf_key = self.obfuscateApiKey()
    headers = {'Content-Type' :  'application/json',
               'cache-control': 'no-cache'}
    body = {
      'apiKey': obf_key,
      'username': self.username,
      'password': self.password,
      'timestamp': timestamp,
    }
    body = json.dumps(body)
    method = 'POST'

    try:
      request = self._api_call(api_path, method, headers=headers, body=body)
      if request.cookies['JSESSIONID']:
        logger.debug("Setting JSESSIONID Variable")
        self.jsessionid = "JSESSIONID={}".format(request.cookies['JSESSIONID'])
        return request.json()
      else:
        raise Exception
    except Exception as e:
      logger.error("Failed to Login to API")
      return False

  def get_groups(self, search=None, page=None, pageSize=None):
    logger.debug("get_groups module called")
    api_path = '/groups'
    headers = {'Content-Type' :  'application/json',
               'cache-control': 'no-cache',
               'cookie' : self.jsessionid}
    method = 'GET'
    
    try:
      request = self._api_call(api_path, method, headers=headers)
    except Exception as e:
      logger.error("Failed to GetGroups")
      return False
    else:
      return request.json()

  def get_departments(self, name=None, page=None, pageSize=None):
    api_path = '/departments?'
    if pageSize:
      api_path = api_path + "pageSize={}".format(pageSize)
    headers = {'Content-Type' :  'application/json',
               'cache-control': 'no-cache',
               'cookie' : self.jsessionid}
    method = 'GET'
    try:
      request = self._api_call(api_path, method, headers=headers)
    except Exception as e:
      logger.error(e)
    else:
      return request.json()

  def get_user(self, id):
    api_path = '/users/{}'.format(id)
    headers = {'Content-Type' :  'application/json',
               'cache-control': 'no-cache',
               'cookie' : self.jsessionid}
    method = 'GET'
    request = self._api_call(api_path, method, headers=headers)

    return request.json()

  def add_user(self, details):
    api_path = '/users/'
    headers = {'Content-Type' :  'application/json',
               'cache-control': 'no-cache',
               'cookie' : self.jsessionid}
    headers.update(cookie=self.jsessionid)
    method = 'POST'
    body = json.dumps(details)

    request = self._api_call(api_path, method, headers=headers, body=body)

    return request.json()

  def update_user(self, id, details):
    api_path = '/users/{}'.format(id)
    headers = {'Content-Type' :  'application/json',
               'cache-control': 'no-cache',
               'cookie' : self.jsessionid}
    method = 'PUT'
    body = json.dumps(details)

    request = self._api_call(api_path, method, headers=headers, body=body)

    return request.json()

  def get_users(self, name=None, dept=None, group=None, page=None, pageSize=None):
    api_path = '/users'
    query = '?'
    if group:
      api_path = api_path + "{}group={}".format(query, group)
      query = '&'
    if pageSize:
      api_path = api_path + "{}pageSize={}".format(query, pageSize)
    
    headers = {'Content-Type' :  'application/json',
               'cache-control': 'no-cache',
               'cookie' : self.jsessionid}
    method = 'GET'

    request = self._api_call(api_path, method, headers=headers)

    return request.json()

  def bulk_delete_users(self, ids=[]):
    api_path = '/users/bulkDelete'
    headers = {'Content-Type' :  'application/json',
               'cache-control': 'no-cache',
               'cookie' : self.jsessionid}
    body = {}
    body['ids'] = ids
    body = json.dumps(body)
    method = 'POST'
    
    request = self._api_call(api_path, method, headers=headers, body=body)

    return request.json()
  
  def get_status(self):
    api_path = '/status'
    headers = {'Content-Type' :  'application/json',
               'cache-control': 'no-cache',
               'cookie' : self.jsessionid}
    method = 'GET'
    
    request = self._api_call(api_path, method, headers=headers)

    return request.json()
  
  def activate_status(self):
    api_path = '/status/activate'
    headers = {'Content-Type' :  'application/json',
               'cache-control': 'no-cache',
               'cookie' : self.jsessionid}
    method = 'POST'
    
    request = self._api_call(api_path, method, headers=headers)

    return request.json()

  def _api_call(self, api_path, method, body=None, params=None, headers={}, cookies=None):

    url = self._url(api_path)
    attempts, max_attempts = 1, 5
    
    while attempts <= max_attempts:

      try:
        #logger.debug("Headers -- {}".format(headers))
        #logger.debug("Cookies -- {}".format(cookies))
        #logger.debug("Body -- {}".format(body))
        if method == 'GET':
          response = requests.get(url, headers = headers, cookies=cookies, verify=True)
        elif method == 'POST':
          response = requests.post(url, headers = headers, data = body, cookies=cookies, verify=True)
        elif method == 'DELETE':
          response = requests.delete(url, headers = headers, data = body, cookies=cookies, verify=True)
        elif method == 'PUT':
          response = requests.put(url, headers = headers, data = body, cookies=cookies, verify=True)
        else:
          logger.error("Unexpected Method - {}".format(method))
          raise
        if response.ok:
          return response
        elif response.status_code == 429:
          timeout_string = json.loads(response.text)
          retry_duration = int(re.findall(r'\d+', timeout_string['Retry-After'])[0])
          logger.info("Waiting {} seconds".format(retry_duration))
          logger.error(response.text + "\n" + str(response.headers))
          time.sleep(retry_duration + 5)
        elif response.status_code == 401:
          logger.debug("401 received - calling authenticate")
          if self.login():
            logger.debug("updating cookie")
            headers.update(cookie=self.jsessionid)
          continue
        else:
          logger.debug("{} - {} - {}".format(response, response.status_code, response.text))
          raise Exception
      except requests.exceptions.RequestException as e:
        logger.error(e)
      except Exception:
        logger.error("Error During API Call - {} ({}/{}) - Please review debug logs.".format(api_path, attempts, max_attempts))
      finally:
        attempts = attempts + 1

class helper:

  def __init__(self):
    self.logger = logging.getLogger('zia_helper')

  def pull_all_zia_data(self, zia):
    self.logger.info("Zscaler Helper -  Pulling All User/Group Data")
    num_results = 200000
    self.zscaler_users = zia.get_users(pageSize=num_results)
    self.zscaler_departments = zia.get_departments(pageSize=10000)
    self.zscaler_groups = zia.get_groups()
    self.logger.info("Zscaler API - Data Pull Complete")
    return self.zscaler_users, self.zscaler_departments, self.zscaler_groups
  
  def modify_zscaler_user(self, zia, user, group, function):
    self.logger.debug("Zscaler Helper - Modify Zscaler User")
    #self.logger.debug("User - {}, Group - {}".format(user,group))
    existing_zscaler_user = [x for x in self.zscaler_users if x['email'].lower() == user['userPrincipalName'].lower()]
    if len(existing_zscaler_user) == 1:
      self.logger.debug("User Found - {}".format(existing_zscaler_user))
      existing_zscaler_user = existing_zscaler_user[0]
      get_updated_user_details = zia.get_user(existing_zscaler_user['id'])
      self.logger.debug("Details Pulled - {}".format(get_updated_user_details))
      if user['userPrincipalName'].lower() == get_updated_user_details['email'].lower():
        none_group =  [x for x in self.zscaler_groups if x['name'].lower() == 'None'.lower()]
        if get_updated_user_details['groups'][0] == {'id': 0}:
          get_updated_user_details['groups'].pop(0)
        if function == 'remove':
          get_updated_user_details['groups'].remove({'id': group['id'], 'name': group['name']})
          if len(get_updated_user_details['groups']) < 1:
            self.logger.debug("Need to add user to None group")
            self.logger.debug(none_group)
            get_updated_user_details['groups'].append({'id': none_group[0]['id'], 'name': none_group[0]['name']})
        elif function == 'add':
          if len(get_updated_user_details['groups']) > 0:
            if any(nonegroup.get('id') == none_group[0]['id'] for nonegroup in get_updated_user_details['groups']):
              get_updated_user_details['groups'].remove({'id': none_group[0]['id'], 'name': none_group[0]['name']})
          get_updated_user_details['groups'].append({'id': group['id'], 'name': group['name']})
        else:
          self.logger.error("Unknown function requested")
          raise
        if 'department' not in get_updated_user_details:
          self.logger.debug("Need to add user to NONE department")
          none_department = [x for x in self.zscaler_departments if x['name'].lower() == 'NONE'.lower()]
          department = {}
          department['id'] = none_department[0]['id']
          department['name'] = none_department[0]['name']
          get_updated_user_details['department'] = department
        get_updated_user_details['comments'] = "3M Automation Modified User - {} UTC".format(datetime.datetime.utcnow().strftime("%Y/%m/%d, %H:%M:%S"))
        self.logger.debug("Details to be sent to Zscaler - {}".format(get_updated_user_details))
        try:
          zia.update_user(get_updated_user_details['id'], get_updated_user_details)
          return True
        except ValueError:
          print("Update api call failed for {}".format(user))
    else:
      self.logger.debug("User {} doesn't exist in Zscaler".format(user['userPrincipalName'].lower()))
      return False