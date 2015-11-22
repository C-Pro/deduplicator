import unittest
import requests


class DupApiTest(unittest.TestCase):

    base_url = 'http://localhost:8000/'

    def test_api_wrong(self):
        r = requests.get(self.base_url + '/something')
        self.assertEqual(r.status_code,
                         400,
                         'Should return 400 \
                         for wrong requests')

    def test_api_true_initial(self):
        r = requests.get(self.base_url + '/2/1')
        self.assertEqual(r.status_code,
                         200,
                         'Should return 200 \
                         for good requests')
        self.assertEqual(r.json()["duplicates"],
                         True,
                         'Users 1 and 2 are duplicates')

    def test_api_false_initial(self):
        r = requests.get(self.base_url + '/3/1')
        self.assertEqual(r.status_code,
                         200,
                         'Should return 200 \
                         for good requests')
        self.assertEqual(r.json()["duplicates"],
                         False,
                         'Users 1 and 3 are not duplicates')

    def test_api_true_secondary(self):
        r = requests.get(self.base_url + 'kozyamba/1002/1001')
        self.assertEqual(r.status_code,
                         200,
                         'Should return 200 \
                         for good requests')
        self.assertEqual(r.json()["duplicates"],
                         True,
                         'Users 1001 and 1002 are duplicates')

    def test_api_false_secondary(self):
        r = requests.get(self.base_url + 'bumburum/1000/1001')
        self.assertEqual(r.status_code,
                         200,
                         'Should return 200 \
                         for good requests')
        self.assertEqual(r.json()["duplicates"],
                         False,
                         'Users 1000 and 1001 \
                         are not duplicates')
