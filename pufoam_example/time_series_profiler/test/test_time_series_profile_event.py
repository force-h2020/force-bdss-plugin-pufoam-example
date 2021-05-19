from unittest import TestCase

from pufoam_example.time_series_profiler.time_series_profiler_model import (
    TimeSeriesEvent)


class TestTimeSeriesProfileEvent(TestCase):

    def setUp(self):
        self.event = TimeSeriesEvent()

    def test_serialize(self):
        self.assertDictEqual(
            {'time_series': [[], []]},
            self.event.serialize()
        )

        self.event.name = 'pufoam_height'
        self.event.time_series = [
            [0, 1, 2, 3],
            [4, 5, 6, 7]
        ]

        self.assertDictEqual(
            {'pufoam_height': [[0, 1, 2, 3],
                               [4, 5, 6, 7]]},
            self.event.serialize()
        )
