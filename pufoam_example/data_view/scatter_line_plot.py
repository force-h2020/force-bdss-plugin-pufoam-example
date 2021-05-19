import numpy as np

from chaco.api import HPlotContainer, GridPlotContainer
from chaco.api import Plot as ChacoPlot
from chaco.tools.api import PanTool
from chaco.tools.api import BetterSelectingZoom as ZoomTool
from traits.api import (
    Str, Instance, Dict, Int, Property,
    HasStrictTraits, on_trait_change, List, Tuple)

from force_wfmanager.ui.review.scatter_plot import ScatterPlot


class LinePlotConfig(HasStrictTraits):

    title = Str

    x_label = Str

    y_label = Str

    line_config = Dict(Str, Dict)


class ScatterLinePlot(ScatterPlot):

    line_title = Str

    line_plot_configs = List(LinePlotConfig)

    #: Reference to axis with line plot
    _line_plots = List(Instance(ChacoPlot))

    _grid_shape = Property(Tuple(Int, Int))

    def customize_plot(self, plot):
        super().customize_plot(plot)
        self._add_line_plots(plot)

    def customize_plot_data(self, plot_data):
        """Extends plot data objects to add a dimension for the curve"""
        super().customize_plot_data(plot_data)
        for line_plot in self.line_plot_configs:
            for name in line_plot.line_config.keys():
                plot_data.set_data(f"x_line_{name}", [])
                plot_data.set_data(f"y_line_{name}", [])
        return plot_data

    def _get__grid_shape(self):
        n_plots = len(self.line_plot_configs)
        shape = [1, 1]
        index = 1
        while np.prod(shape) < n_plots:
            shape[index] += 1
            index = (index + 1) % 2
        return tuple(shape)

    @on_trait_change("analysis_model:step_metadata[],"
                     "analysis_model.selected_step_indices")
    def request_update(self):
        # Listens to the change in data points in the analysis model.
        # Enables the plot update at the next cycle.
        self.update_required = True

    def _update_line_plot(self, metadata):
        """Updates a line plot. Will attempt to interpolate a curve through
        the 2D data, and flag an error to display in the UI if fails.
        """
        if (
                self.x == ""
                or self.y == ""
                or self.analysis_model.is_empty
                or self.analysis_model.selected_step_indices is None
        ):
            x_data = []
            y_data = []

        else:
            index = self.analysis_model.selected_step_indices[0]
            data = self.analysis_model.step_metadata[index]
            try:
                x_data = data[metadata][0]
                y_data = data[metadata][1]
            except KeyError:
                x_data = []
                y_data = []

        self._plot_data.set_data(f'x_line_{metadata}', x_data)
        self._plot_data.set_data(f'y_line_{metadata}', y_data)

    def _recenter_x_line_axis(self, metadata, line_plot):
        """ Resets the bounds on the x-axis of the plot. If now x axis
        is specified, uses the default bounds (-1, 1). Otherwise, infers
        the bounds from the x-axis related data."""
        if len(metadata) == 0:
            bounds = (-1, 1)
        else:
            bounds = (np.inf, -np.inf)
            for name in metadata.keys():
                data = self._plot_data.get_data(f"x_line_{name}")
                if len(data) > 0:
                    line_bounds = self.calculate_axis_bounds(data)
                    bounds = (min(line_bounds[0], bounds[0]),
                              max(line_bounds[1], bounds[1]))
        self._set_plot_x_range(line_plot, *bounds)
        self._reset_zoomtool(line_plot)
        return bounds

    def _recenter_y_line_axis(self, metadata, line_plot):
        """ Resets the bounds on the x-axis of the plot. If now y axis
        is specified, uses the default bounds (-1, 1). Otherwise, infers
        the bounds from the y-axis related data."""
        if len(metadata) == 0:
            bounds = (-1, 1)
        else:
            bounds = (np.inf, -np.inf)
            for name in metadata.keys():
                data = self._plot_data.get_data(f"y_line_{name}")
                if len(data) > 0:
                    line_bounds = self.calculate_axis_bounds(data)
                    bounds = (min(line_bounds[0], bounds[0]),
                              max(line_bounds[1], bounds[1]))
        self._set_plot_y_range(line_plot, *bounds)
        self._reset_zoomtool(line_plot)
        return bounds

    def _add_line_plots(self, plot):
        """Adds curve line plots to the ChacoPlot"""

        line_plots = []
        for plot_config in self.line_plot_configs:
            line_plot = ChacoPlot(self._plot_data)

            # Customize text
            line_plot.trait_set(
                title=plot_config.title, padding=75, line_width=1)
            line_plot.x_axis.title = plot_config.x_label
            line_plot.y_axis.title = plot_config.y_label

            # Add pan and zoom tools
            line_plot.tools.append(PanTool(line_plot))
            line_plot.overlays.append(ZoomTool(line_plot))

            for name, kwargs in plot_config.line_config.items():
                line = line_plot.plot(
                    (f"x_line_{name}", f"y_line_{name}"),
                    type="line",
                    **kwargs
                )[0]
                self._sub_axes[f'{name}_line_plot'] = line

            line_plots.append(line_plot)

        container = GridPlotContainer(
            *line_plots,
            shape=self._grid_shape,
            spacing=(0, 0),
            valign='top',
            bgcolor="none"
        )
        self._component = HPlotContainer(
            plot, container,
            bgcolor="none"
        )
        self._line_plots = line_plots

    def update_data_view(self):
        """Overloads the parent class method to update the curve plot"""
        super(ScatterLinePlot, self).update_data_view()
        for plot_config in self.line_plot_configs:
            for metadata in plot_config.line_config.keys():
                self._update_line_plot(metadata)

    @on_trait_change("analysis_model.selected_step_indices", post_init=True)
    def _update_line_plot_axis(self):
        """Overload the parent class method to update the curve plot"""
        for index, plot_config in enumerate(self.line_plot_configs):
            for metadata in plot_config.line_config.keys():
                self._update_line_plot(metadata)

            line_plot = self._line_plots[index]
            metadata = plot_config.line_config
            self._recenter_x_line_axis(metadata, line_plot)
            self._recenter_y_line_axis(metadata, line_plot)
