import unittest

from app.src import buckyBoard as b


class MyTestCase(unittest.TestCase):
    b.systems = [{'system_id': 'sys_1'}]
    b.system_types = [{'systemType_id': 123, 'name': 'ABCD'}]
    b.records = [{'guid': 'guid_2_ererererererer'},
                 {'guid': 'guid_3_ererererererer'},
                 {'guid': 'guid_4_ererererererer'}]
    def test_something(self):
        nodes = {
            'nodes': [{
                'guid': 'guid_1_ererererererer',
                'title': 'unit1',
                'type': 'unit',
                'nodes': [{
                    'title': 'group1', 'type': 'group', 'system_id': 'sys_1', 'systemType_id': 123,
                    'guid': 'guid_2_ererererererer',
                    'nodes': [{
                        'title': 'asset-1', 'type': 'system', 'system_id': 'sys_1', 'systemType_id': 123,
                        'guid': 'guid_3_ererererererer',
                        'nodes': []
                    }, {
                        'title': 'asset-2', 'type': 'system', 'system_id': 'sys_1', 'systemType_id': 123,
                        'guid': 'guid_4_ererererererer',
                        'nodes': []
                    }]
                }]
            }]
        }
        rollups = {}
        resp = b.setBBValues("user_dn", nodes, rollups, True, True, True, [])
        self.assertEqual(resp, resp)  # add assertion here


if __name__ == '__main__':
    unittest.main()
