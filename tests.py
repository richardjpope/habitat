import json
import unittest
from habitat import app

class TestHabitat(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_entry(self):

        data = {"id": "530cd73044c01ce9cffa4d9d", "latlng": {"coordinates": [0.32,0.32], "type": "Point"}, "occured_at": "2014-02-24T16:26:11.059000"}
        rv = self.app.post('/locations', data=json.dumps(data), content_type='application/json')
        self.assertEqual(rv.status_code, 201)

if __name__ == '__main__':
    unittest.main()
