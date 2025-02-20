import unittest

from app.src import buckyBoard as b


class MyTestCase(unittest.TestCase):
    b.systems = [{'system_id': 'sys_1'}]
    b.system_types = [{'systemType_id': 123, 'name': 'ABCD'}]
    b.records = [{'guid': 'guid_2_ererererererer', 'record_id': 100001, 'tracking_id': 99930},
                 {'guid': 'guid_3_ererererererer', 'record_id': 100002, 'tracking_id': 99930},
                 {'guid': 'guid_4_ererererererer', 'record_id': 100003, 'tracking_id': 99930}]
    def test_something(self):
        nodes = {
            'nodes': [{
                'guid': 'guid_1_ererererererer',
                'title': 'unit1',
                'type': 'unit',
                'nodes': [{
                    'title': 'group1', 'type': 'group', 'system_id7': 'sys_1', 'systemType_id': 123,
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
