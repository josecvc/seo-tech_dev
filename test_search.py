import unittest, time

from main import search_moby

class TestSearch(unittest.TestCase):
    def tearDown(self):
        time.sleep(1)

    def test_valid_search(self):
        self.assertEqual(search_moby("Prince of Persia"), True)

    def test_invalid_search(self):
        self.assertEqual(search_moby("dijafsfdkfask"), False)