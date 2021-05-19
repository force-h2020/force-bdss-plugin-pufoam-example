import unittest

from force_bdss.api import DataValue

from pufoam_example.utilities import parse_data_values


class UtilitiesTestCase(unittest.TestCase):

    def setUp(self):
        self.data_values = [
            DataValue(value=1, type='foo'),
            DataValue(value=3, type='bar'),
            DataValue(value=2, type='foo'),
        ]

    def test_parse_data_values(self):

        foos = parse_data_values(self.data_values, 'foo')
        bars = parse_data_values(self.data_values, 'bar')

        self.assertEqual(2, len(foos))
        self.assertListEqual([1, 2], foos)

        self.assertEqual(1, len(bars))
        self.assertListEqual([3], bars)
