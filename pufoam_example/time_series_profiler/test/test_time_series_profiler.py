from unittest import TestCase

import numpy as np

from traits.testing.unittest_tools import UnittestTools

from force_bdss.api import DataValue

from pufoam_example.time_series_profiler.time_series_profiler_factory import (
    TimeSeriesProfilerFactory)
from pufoam_example.tests.fixtures.fixtures_path import get


class TestTimeSeriesProfiler(TestCase, UnittestTools):

    def setUp(self):
        self.factory = TimeSeriesProfilerFactory(
            plugin={'id': '0', 'name': 'test'})
        self.data_source = self.factory.create_data_source()
        self.model = self.factory.create_model()
        self.height_profile = np.load(
            get('test_height_profile.npy')
        )
        self.temp_profile = np.load(
            get('test_height_profile.npy')
        )
        self.x_data = [0.1, 0.2, 0.3, 0.4, 1.0]

    def test_fit_to_curve(self):
        y_data = np.tanh(self.x_data)

        func = self.data_source._fit_to_curve(self.x_data, y_data)
        self.assertTrue(
            np.allclose(
                np.array([0.09966, 0.19737, 0.29131,
                          0.37994, 0.76159]),
                func(self.x_data).tolist(),
                rtol=1.e-4
            )
        )

    def test_get_reference_data(self):
        data = self.data_source._get_reference_data(self.model)

        self.assertEqual(1, len(data))
        headers = ['time[s]', 'height[mm]', 'temperature[K]']
        for header in headers:
            self.assertIn(header, data[0])
            self.assertEqual(55, len(data[0][header]))
            self.assertTrue(np.float, data[0][header].dtype)

    def test_calculate_residuals(self):
        ref_data = np.array(
            [self.x_data,
             np.tanh(self.x_data)]
        )
        sim_data = np.array(
            [[0.11, 0.19, 0.32, 0.41],
             [0.09, 0.20, 0.42, 0.69]]
        )

        self.assertAlmostEqual(
            0.4464845,
            self.data_source.calculate_residuals(
                sim_data, ref_data),
            5
        )

        sim_data = np.array(
            [[0.11, 0.19, 0.32, 1.1],
             [0.09, 0.20, 0.42, 0.69]]
        )
        self.assertAlmostEqual(
            0.14279425,
            self.data_source.calculate_residuals(
                sim_data, ref_data),
            5
        )

    def test_changes_slots(self):
        model = self.factory.create_model()

        slots = self.data_source.slots(model)
        self.assertEqual(2, len(slots[0]))
        self.assertEqual(2, len(slots[1]))

        model.input_method = 'Parameter'

        slots = self.data_source.slots(model)
        self.assertEqual(4, len(slots[0]))
        self.assertEqual(2, len(slots[1]))

    def test_basic_function(self):

        model = self.factory.create_model()
        data_values = [DataValue(value=self.height_profile),
                       DataValue(value=self.temp_profile)]

        with self.assertTraitChanges(model, "event", count=2):
            res = self.data_source.run(model, data_values)

        self.assertEqual("RESIDUALS", res[0].type)
        self.assertEqual("RESIDUALS", res[1].type)

        model.input_method = 'Parameter'
        data_values += [
            DataValue(value=self.height_profile),
            DataValue(value=self.temp_profile)
        ]
        res = self.data_source.run(model, data_values)
        self.assertEqual("RESIDUALS", res[0].type)
        self.assertEqual("RESIDUALS", res[1].type)

    def test_notify_time_series(self):
        height_profile = [[], []]
        with self.assertTraitChanges(self.model, "event", count=1):
            self.model.notify_time_series(height_profile)

        with self.assertTraitChanges(self.model, "event", count=1):
            self.model.notify_time_series(
                np.array(height_profile)
            )
