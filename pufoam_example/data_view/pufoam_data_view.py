from traits.api import Instance
from traitsui.api import (
    HGroup, UItem, View
)

from .scatter_line_plot import ScatterLinePlot, LinePlotConfig


class PUFoamDataView(ScatterLinePlot):

    title = 'PUFoam Data View'

    description = "PUFoam data line plot"

    results_plot = Instance(ScatterLinePlot)

    def default_traits_view(self):
        return View(
            HGroup(
                UItem("results_plot", style='custom'),
                scrollable=True
            )
        )

    def _results_plot_default(self):
        """Returns a curve plot with synced variables for the axis
        on display.
        """
        height_plot = LinePlotConfig(
            title='Foam Height',
            x_label='Time (s)',
            y_label='Height (mm)',
            line_config={
                'height_profile': {
                    'line_style': 'solid',
                    'color': 'red'
                },
                'ref_height_profile': {
                    'line_style': 'dash',
                    'color': 'black'
                }
            }
        )
        temp_plot = LinePlotConfig(
            title='Foam Temperature',
            x_label='Time (s)',
            y_label='Temperature (K)',
            line_config={
                'temp_profile': {
                    'line_style': 'solid',
                    'color': 'red'
                },
                'ref_temp_profile': {
                    'line_style': 'dash',
                    'color': 'black'
                }
            }
        )
        plot = ScatterLinePlot(
            title='PUFoam Fitting Data',
            line_plot_configs=[height_plot, temp_plot],
            analysis_model=self.analysis_model,
            is_active_view=self.is_active_view
        )
        self.sync_trait("is_active_view", plot)
        return plot
