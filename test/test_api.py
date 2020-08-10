#!/usr/bin/env python

from zscalertools import api
import logging
import unittest

logging.basicConfig(level=logging.DEBUG)

class TestSequenceFunctions(unittest.TestCase):
  def setUp(self):
    self.api = api.zia('admin.zscalerbeta.net', 'test_api@mmm.com', 'e6T6CC#!Qy!6m4bJR9G', '3JrrIbUVDrLr')
    
  def test_login(self):
    self.api.login()
    self.assertEqual(self.api, True)

    
if __name__ == "__main__":
  unittest.main()