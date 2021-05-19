from unittest import TestCase

from force_wfmanager.model.analysis_model import AnalysisModel

from pufoam_example.data_view.pufoam_data_view import (
    PUFoamDataView)


class TestPUFoamDataView(TestCase):

    def setUp(self):
        self.analysis_model = AnalysisModel(
            header=['parameter_1', 'parameter_2',
                    'kpi_1'],
            _evaluation_steps=[('A', 1.45, 10),
                               ('A', 5.11, 12),
                               ('B', 4.999, 17),
                               ('B', 4.998, 22)],
            _step_metadata=[
                {
                    'height_profile': [
                        [0, 1, 2, 3, 4, 5],
                        [0.1, 0.2, 0.4, 0.7, 0.8, 0.9]
                    ]
                },
                {
                    'height_profile': [
                        [0, 1, 2, 3, 4, 5],
                        [0.1, 0.2, 0.4, 0.7, 0.8, 0.9]
                    ],
                    'ref_height_profile': [
                        [0, 1.1, 2.2, 3.3, 4.4, 5.5],
                        [0.11, 0.22, 0.5, 0.7, 0.8, 0.9]
                    ]
                },
                {
                    'height_profile': [
                        [0, 1, 2, 3, 4, 5],
                        [0.1, 0.2, 0.4, 0.7, 0.8, 0.9]
                    ],
                    'ref_height_profile': [
                        [0, 0.9, 2, 3, 3.8, 5.2],
                        [0.14, 0.24, 0.6, 0.71, 0.84, 0.97]
                    ],
                    'temp_profile': [
                        [0, 1, 2, 3, 4, 5],
                        [0.1, 0.2, 0.4, 0.7, 0.8, 0.9]
                    ],
                    'ref_temp_profile': [
                        [0, 0.9, 2, 3, 3.8, 5.2],
                        [0.14, 0.24, 0.6, 0.71, 0.84, 0.97]
                    ]
                }, {}]
        )
        self.data_view = PUFoamDataView(
            analysis_model=self.analysis_model
        )

    def test_plot_data(self):
        arrays = ['x', 'y', 'color_by',
                  "x_line_height_profile",
                  "y_line_height_profile",
                  "x_line_ref_height_profile",
                  "y_line_ref_height_profile",
                  "x_line_temp_profile",
                  "y_line_temp_profile",
                  "x_line_ref_temp_profile",
                  "y_line_ref_temp_profile"
                  ]

        for key in arrays:
            self.assertEqual(
                0, len(self.data_view.results_plot._plot_data.arrays[key]))
