from unittest import TestCase

from force_wfmanager.model.analysis_model import AnalysisModel

from pufoam_example.data_view.scatter_line_plot import (
    ScatterLinePlot, LinePlotConfig)


class TestScatterLinePlot(TestCase):

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
                    'curve_1': [
                        [0, 1, 2, 3, 4, 5],
                        [0.1, 0.2, 0.4, 0.7, 0.8, 0.9]
                    ]
                },
                {
                    'curve_1': [
                        [0, 1, 2, 3, 4, 5],
                        [0.1, 0.2, 0.4, 0.7, 0.8, 0.9]
                    ],
                    'curve_2': [
                        [0, 1, 2, 3, 4, 5],
                        [0.11, 0.19, 0.3, 0.6, 0.7, 0.8]
                    ]
                }, {}, {}
            ]
        )
        curve_plot = LinePlotConfig(
            title='Dummy data',
            x_label='Time (s)',
            y_label='Height (mm)',
            line_config={
                'curve_1': {
                    'line_style': 'solid',
                    'color': 'red'
                },
                'curve_2': {
                    'line_style': 'dash',
                    'color': 'black'
                }
            }
        )
        self.plot = ScatterLinePlot(
            line_title='Metadata',
            analysis_model=self.analysis_model,
            line_plot_configs=[curve_plot],
        )

    def test_init(self):
        self.assertNotEqual(
            self.plot._component, self.plot._plot)
        self.assertIsNotNone(self.plot._axis)
        self.assertEqual(1, len(self.plot._line_plots))
        self.assertEqual(2, len(self.plot._sub_axes))
        self.assertEqual((1, 1), self.plot._grid_shape)

    def test_grid_shape(self):
        self.plot.line_plot_configs.append(LinePlotConfig())
        self.assertEqual((1, 2), self.plot._grid_shape)

        self.plot.line_plot_configs.append(LinePlotConfig())
        self.assertEqual((2, 2), self.plot._grid_shape)

        self.plot.line_plot_configs.append(LinePlotConfig())
        self.assertEqual((2, 2), self.plot._grid_shape)

    def test_customize_plot_data(self):
        arrays = ['x', 'y', "color_by",
                  "x_line_curve_1", "y_line_curve_1",
                  "x_line_curve_2", "y_line_curve_2"]
        for key in arrays:
            self.assertEqual(
                0, len(self.plot._plot_data.arrays[key]))

    def test_update_line_plot_axis(self):
        self.plot.x = 'parameter_2'
        self.plot.y = 'kpi_1'
        self.analysis_model.selected_step_indices = [1]
        self.assertEqual(
            6, len(self.plot._plot_data.get_data("x_line_curve_1")))
        self.assertEqual(
            6, len(self.plot._plot_data.get_data("y_line_curve_1")))

    def test_update_line_plot(self):
        self.assertFalse(self.plot.analysis_model.is_empty)
        self.plot._update_line_plot("curve_1")
        self.assertEqual(
            0, len(self.plot._plot_data.get_data("x_line_curve_1")))
        self.assertEqual(
            0, len(self.plot._plot_data.get_data("y_line_curve_1")))

        self.plot.x = 'parameter_2'
        self.plot.y = 'kpi_1'
        self.analysis_model.selected_step_indices = [1]
        self.plot._update_line_plot("curve_1")
        self.assertEqual(
            6, len(self.plot._plot_data.get_data("x_line_curve_1")))
        self.assertEqual(
            6, len(self.plot._plot_data.get_data("y_line_curve_1")))

        self.analysis_model.selected_step_indices = [2]
        self.plot._update_line_plot("curve_1")
        self.assertEqual(
            0, len(self.plot._plot_data.get_data("x_line_curve_1")))
        self.assertEqual(
            0, len(self.plot._plot_data.get_data("y_line_curve_1")))
