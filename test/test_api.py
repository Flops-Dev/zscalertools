#!/usr/bin/env python

from zscalertools import api
import logging
import yaml
import unittest

logging.basicConfig(level=logging.DEBUG)

stream = open('test_api.yml', yaml.SafeLoader)

class TestSequenceFunctions(unittest.TestCase):
  def setUp(self):
    self.api = api.zia(config['url'], config['username'], config['password'], config['cloud_api_key'])
    
  def test_login(self):
    login = self.api.login()
    self.assertEqual(login['authType'], 'ADMIN_LOGIN')

    
if __name__ == "__main__":
  unittest.main()