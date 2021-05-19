import numpy as np
from scipy import interpolate

from force_bdss.api import BaseDataSource, DataValue, Slot

from .ref_data import get, load_data_set, load_formulation


class TimeSeriesProfilerDataSource(BaseDataSource):
    """Class that calculates fit to reference data
    """

    def _fit_to_curve(self, x_data, y_data):
        """Fit sigmoid curve to height curve and return a parameterised
        function that just requires time inputs to calculate fitted
        height values. At the moment we just try
        fitting to one function, but this could be varied in the future.

        Parameters
        ----------
        x_data, y_data: ndarray
            Numpy arrays containing X and Y data to fit
        """
        return interpolate.interp1d(x_data, y_data)

    def _get_reference_data(self, model):
        """Load reference data set for Formulation of interest"""
        formulation_data = load_formulation(model.reference_model)
        data_sets = formulation_data["data_sets"]
        data = [
            load_data_set(get(data_set['data_file']))
            for data_set in data_sets
        ]
        return data

    def calculate_residuals(self, sim_data, ref_data):
        """Calculate total difference between simulated and
        reference height time series. This is first achieved by
        fitting the reference data to a sigmoid curve in order
        to generate data values that have the same time component
        as those produced by the simulation.

        Parameters
        ----------
        sim_data, ref_data: ndarray
           Simulation and reference data sets, supplied as 2D
           Numpy arrays
        """
        func = self._fit_to_curve(*ref_data)

        # Only include x values within the interpolation range
        x_data, y_data = sim_data
        indices = np.where(x_data <= max(ref_data[0]))

        data_points = func(x_data[indices])
        residuals = abs(y_data[indices] - data_points).sum()

        return residuals

    def run(self, model, parameters):
        """Compares a PUFoam height and temperature time series with a
        reference data set stored on file. Can either handle input
        reference data on the model or as an MCO parameter.

        Expects the height values in parameters to be reported from the
        Workflow in meters and temperature values to be reported in Kelvin
        """

        height_profile = parameters[0].value
        temp_profile = parameters[1].value

        if model.input_method == 'Model':
            ref_data = self._get_reference_data(model)
            x_data = ref_data[0]['time[s]']
            height_data = ref_data[0]['height[mm]'] * 1e-3

            if 'temperature[C]' in ref_data[0]:
                # Convert any temperature data in celsius to Kelvin
                temp_data = ref_data[0]['temperature[C]'] + 273
            else:
                temp_data = ref_data[0]['temperature[K]']
        else:
            ref_data = parameters[2].value
            x_data, height_data = np.array(ref_data)
            ref_data = parameters[3].value
            x_data, temp_data = np.array(ref_data)

        # Notify reference data sets to any listeners present
        model.notify_time_series(
            np.array([x_data, height_data]),
            name='ref_height_profile'
        )
        model.notify_time_series(
            np.array([x_data, temp_data]),
            name='ref_temp_profile'
        )

        # Calculate residuals between simulation and reference data sets
        # for both time series
        height_residuals = self.calculate_residuals(
            height_profile, (x_data, height_data)
        )
        temp_residuals = self.calculate_residuals(
            temp_profile, (x_data, temp_data)
        )

        return [DataValue(type="RESIDUALS", value=height_residuals),
                DataValue(type="RESIDUALS", value=temp_residuals)]

    def slots(self, model):

        input_slots = (
            Slot(
                type="FOAM_HEIGHT",
                description="Simulated height profile of PU foam as "
                            "time series",
            ),
            Slot(
                type="FOAM_TEMPERATURE",
                description="Simulated temperature profile of PU foam as "
                            "time series",
            ),
        )

        if model.input_method == 'Parameter':
            input_slots += (
                Slot(
                    type="FOAM_HEIGHT",
                    description="Reference height profile of PU foam as "
                                "time series",
                ),
                Slot(
                    type="FOAM_TEMPERATURE",
                    description="Reference temperature profile of PU foam as "
                                "time series",
                )
            )

        return (
            input_slots,
            (
                Slot(
                    type="RESIDUALS",
                    description="Residuals from height "
                                "reference data"
                ),
                Slot(
                    type="RESIDUALS",
                    description="Residuals from temperature "
                                "reference data"
                ),
            ),
        )
