from tempfile import NamedTemporaryFile
from unittest import TestCase

import numpy as np

from force_bdss.api import MCOStartEvent

from pufoam_example.csv_writer.pufoam_csv_writer import PUFoamCSVWriterFactory
from pufoam_example.time_series_profiler.time_series_profiler_model import (
    TimeSeriesEvent)


class TestPUFoamCSVWriter(TestCase):

    def setUp(self):
        self.factory = PUFoamCSVWriterFactory(
            plugin={'id': '0', 'name': 'test'})
        self.model = self.factory.create_model(
            model_data={
                'extra_columns': ['BSD']
            }
        )
        self.listener = self.factory.create_listener()
        self.start_event = MCOStartEvent(
            parameter_names=['test_param'],
            kpi_names=['test_kpi']
        )

    def test_parse_start_event(self):
        # Given
        self.listener.initialize(self.model)

        # Then
        self.assertListEqual(
            ['test_param', 'test_kpi', 'BSD'],
            self.listener.parse_start_event(self.start_event)
        )

    def test_deliver(self):
        # Given
        time_series = [np.arange(10).tolist(),
                       np.arange(10).tolist()]

        with NamedTemporaryFile() as tmp_file:
            self.model.path = tmp_file.name
            self.listener.initialize(self.model)

            with self.subTest('Assert header is contains additional '
                              'columns.'):
                # When
                self.listener.deliver(self.start_event)
                # Then
                self.assertListEqual(
                    ['test_param', 'test_kpi', 'BSD'],
                    self.listener.header
                )
                self.assertDictEqual(
                    {'test_param': None,
                     'test_kpi': None,
                     'BSD': None},
                    self.listener.row_data
                    )
            with self.subTest('Assert time series data is added.'):
                time_event = TimeSeriesEvent(
                    time_series=time_series,
                    name='bsd_profile'
                )
                self.listener.deliver(time_event)
                self.assertDictEqual(
                    {'test_param': None,
                     'test_kpi': None,
                     'BSD': 9},
                    self.listener.row_data
                )
