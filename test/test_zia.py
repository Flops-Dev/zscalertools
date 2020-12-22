#!/usr/bin/env python

from zscalertools import zia
import logging
import yaml
import unittest
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)

stream = open(Path(__file__).parent / 'test_api.yml', 'r')
config = yaml.load(stream, yaml.SafeLoader)
stream.close()

class TestSequenceFunctions(unittest.TestCase):
  def setUp(self):
    self.api = zia.api(config['url'], config['username'], config['password'], config['cloud_api_key'])
    
  def test_login_logout(self):
    login = self.api.login()
    self.assertEqual(login['authType'], 'ADMIN_LOGIN')
    logout = self.api.logout()
    self.assertEqual(logout['status'], 'success')
  
  def test_locations_lite(self):
    locations_lite = self.api.get_locations_lite()
    self.assertTrue('id', locations_lite)

  def test_locations(self):
    locations = self.api.get_locations()
    self.assertTrue('id', locations)
    for location in locations:
      if 'childCount' in location:
        sub_location = self.api.get_sublocations(location['id'])
        self.assertTrue('id', sub_location)

if __name__ == "__main__":
  unittest.main()