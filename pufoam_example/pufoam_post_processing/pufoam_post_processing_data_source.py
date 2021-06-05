import numpy as np
from scipy.optimize import curve_fit

from force_bdss.api import BaseDataSource, DataValue, Slot

from pufoam_example.utilities import tanh_curve


class PUFoamPostProcessingDataSource(BaseDataSource):
    """Class calculates bubble size distribution (BSD) of PU foam as
    a function of time
    """

    def _fit_to_curve(self, x_data, y_data):
        """Fit sigmoid curve to truncated trajectory and return the
        maximum value of the fitted curve. At the moment we just try
        fitting to one function, but this could be varied in the future.
        """
        popt, _ = curve_fit(tanh_curve, x_data, y_data)
        return {
            key: value for key, value in zip(
                ["x0", "y0", "y1", "b"], popt
            )
        }

    def projected_height_profile(self, x_data, y_data, thresh=1E-3):
        """Calculate projected height profile, based on simulation data.
        This is used mainly for display purposes and is not passed as
        an output variable from the data source."""

        # Fit the data to a curve function in order to extrapolate
        try:
            popt = self._fit_to_curve(x_data, y_data)
        except RuntimeError:
            # If the trajectory cannot be fit, simply return the current
            # height profile as the projected data
            return np.array([x_data, y_data])

        # Calculate the initial data points of the fitted curve function
        diff_x = min(np.diff(x_data))
        proj_x_data = [0, diff_x]
        proj_y_data = tanh_curve(
            np.array(proj_x_data), **popt).tolist()

        # Extrapolate until the proejected final height is reached
        while abs(proj_y_data[-1] - popt['y1']) >= thresh:
            proj_x_data += [proj_x_data[-1] + diff_x]
            proj_y_data += [tanh_curve(proj_x_data[-1], **popt)]

        return np.array([proj_x_data, proj_y_data])

    def calculate_overpacking_fraction(self, markers, data):
        """Extrapolates foam filling trajectory to predict over-packing
        fraction of mesh.
        """

        # Obtain filling fraction trajectory and truncate at point when
        # domain is filled. If running in 'mold-filling' mode, this is
        # when the solver stops and the final result is repeated in putput
        time, traj = self.calculate_filling_fraction(markers, data)

        y_data, indices = np.unique(traj, return_index=True)
        x_data = time[indices] / len(traj)

        # Fit sigmoid curve to truncated trajectory. Overpacking fraction
        # is obtained from curve's maximum value
        try:
            popt = self._fit_to_curve(x_data, y_data)
            max_value = popt['y1']
        except RuntimeError:
            # Return an inf value if the foam has risen too fast
            # to be fit to the curve. Else return the final filling
            # fraction if the foam rose too slowly
            if np.isclose(y_data[-1], 1.0, 1E-2):
                max_value = np.inf
            else:
                max_value = y_data[-1]

        return max_value

    def calculate_filling_fraction(self, markers, data):
        """ Extract the domain average volume filling fraction from the
        simulation data.
        """
        fraction = 1 - data[:, markers.index("volAverage(alpha.gas)")]
        time = data[:, markers.index("Time")]
        return time, fraction

    def calculate_foam_temperature(self, markers, data):
        """ Extract the domain average temperature from the simulation data
        in units of K
        """
        # Raw data is in units of K
        temp = data[:, markers.index("volAverage(TS)")]
        time = data[:, markers.index("Time")]
        return time, temp

    def calculate_viscosity(self, markers, data):
        """ Extract the domain average foam viscosity from the simulation data
        in units of Pa s
        """
        # Note: requires the muFoamCorr variable to be present in the volume
        #  averaged output file. This can be set in the PUFoam control dict
        #  prior to the run, but is not included in the standard installation.
        try:
            viscosity = data[:, markers.index("volAverage(muFoamCorr)")]
        except ValueError:
            # Create some dummy time series data if variable not present
            viscosity = [0] * len(data)

        return viscosity

    def calculate_foam_density(self, markers, data):
        """ Extract the domain average foam density from the simulation data
        in units of kg m-3
        """
        # Raw data is in units of kg m-3
        rho = data[:, markers.index("volAverage(rho_foam)")]
        return rho

    def calculate_foam_bsd(self, markers, data):
        """ Calculate the mean bubble size diameter from the simulation
         data and eq. 11 from [1] in units of μm.

        References
        --------
        [1]: M. Karimi, H. Droghetti, D.L. Marchisio, "PUFoam: A novel
        open-source CFD solver for the simulation of polyurethane foams"
        """

        bubble_size = (
            6.0
            * data[:, markers.index("volAverage(mOne)")]
            / data[:, markers.index("volAverage(mZero)")]
        ) ** (1.0 / 3.0)
        time = data[:, markers.index("Time")]

        return np.array([time, bubble_size])

    def calculate_foam_thermal_conductivity(self, markers, data):
        """ Calculate the foam thermal conductivity from the simulation
         data and eq. 24 from [1] in units of mW m-1 K-1. The number in the
        conductivity expression are given in the paper.

        References
        --------
        [1]: M. Karimi, H. Droghetti, D.L. Marchisio, "PUFoam: A novel
        open-source CFD solver for the simulation of polyurethane foams"
        """
        rho = data[:, markers.index("volAverage(rho_foam)")]

        # Raw data is in units of W m-1 K-1
        conductivity = np.where(
            rho > 48,
            8.7006e-8 * rho ** 2 + 8.4674e-5 * rho + 1.16e-2,
            9.3738e-6 * rho ** 2 - 7.3511e-4 * rho + 2.965e-2,
        )

        # Return value converted to mW m-1 K-1
        return conductivity * 1E3

    def calculate_height_profile(self, markers, data, mesh):
        """Calculates height profile in m for the foam expansion during the
        simulation

        Returns
        -------
        height_profile: array-like
            A 2D array of time (s), height (m) data
        """

        time, filling_fraction = self.calculate_filling_fraction(
            markers, data)

        y_data = np.unique(filling_fraction)
        y_data *= mesh.z_length * mesh.convert_to_meters
        x_data = time[:len(y_data)]

        return np.array([x_data, y_data])

    def calculate_temperature_profile(self, markers, data):
        """Calculates temperature profile in K for the foam expansion during the
        simulation

        Returns
        -------
        height_profile: array-like
            A 2D array of time (s), temperature (K) data
        """

        time, temperature = self.calculate_foam_temperature(
            markers, data)

        y_data = np.unique(temperature)
        x_data = time[:len(y_data)]

        return np.array([x_data, y_data])

    def read_datafile(self, filepath, file_specification):
        """ Reads the volume averaged data from the file, which was generated
        during the PUFoam simulation. File specification tells the structure
        of the file, and where the data of interest is located. We assume the
        structure of the file and then read simulation data for each time step.

        Parameters
        --------
        filepath: str
            Path to the simulation output data file
        file_specification: dict
            File structure specification, which defines how the
            file (and data) should be read

        Return
        --------
        markers: List(str)
            Names of the quantities stored inside the file
        data: np.array
            Data array with simulation quantities, with different quantities
            stored in columns, and rows represent the time snapshots
        """
        with open(filepath) as file:
            n_system_lines = file_specification["n_system_lines"]

            # Skip the first `n_system_lines` that contain system
            # or technical information
            for _ in range(n_system_lines):
                file.readline()

            markers = file.readline()
            # Markers are the string labels of the data columns.
            # The first element is a hash character.
            markers = markers.split()[1:]

            data = np.loadtxt(file)

        return markers, data

    def run(self, model, parameters):

        sim_output_file = parameters[0].value
        mesh = parameters[1].value

        datafile_specification = {"n_system_lines": model.n_system_lines}

        markers, data = self.read_datafile(
            sim_output_file, datafile_specification
        )
        foam_bsd = self.calculate_foam_bsd(markers, data)
        _, foam_filling = self.calculate_filling_fraction(markers, data)
        foam_overpacking = self.calculate_overpacking_fraction(markers, data)
        foam_viscosity = self.calculate_viscosity(markers, data)[-1]
        foam_density = self.calculate_foam_density(markers, data)[-1]
        foam_conductivity = self.calculate_foam_thermal_conductivity(
            markers, data
        )[-1]
        foam_height = self.calculate_height_profile(markers, data, mesh)
        foam_temperature = self.calculate_temperature_profile(markers, data)

        # Broadcast simulation time series to be recorded as metadata
        # for the run
        model.notify_time_series(foam_bsd, name='bsd_profile')
        model.notify_time_series(foam_height, name='height_profile')
        model.notify_time_series(foam_temperature, name='temp_profile')

        return [
            DataValue(type="FOAM_BSD", value=foam_bsd),
            DataValue(type="FILLING_FRACTION", value=foam_filling),
            DataValue(type="OVERPACKING_FRACTION", value=foam_overpacking),
            DataValue(type="FOAM_VISCOSITY", value=foam_viscosity),
            DataValue(type="FOAM_DENSITY", value=foam_density),
            DataValue(type="FOAM_THERM_COND", value=foam_conductivity),
            DataValue(type="FOAM_HEIGHT", value=foam_height),
            DataValue(type="FOAM_TEMPERATURE", value=foam_temperature),
        ]

    def slots(self, model):

        return (
            (
                Slot(
                    type="SIMULATION_OUTPUT",
                    description="Simulation output",
                ),
                Slot(
                    type="MESH",
                    description="Simulation domain",
                ),
            ),
            (
                Slot(
                    type="FOAM_BSD",
                    description="PU foam bubble size distribution",
                ),
                Slot(
                    type="FILLING_FRACTION",
                    description="PU foam filling fraction trajectory",
                ),
                Slot(
                    type="OVERPACKING_FRACTION",
                    description="PU foam overpacking fraction",
                ),
                Slot(
                    type="FOAM_VISCOSITY",
                    description="PU foam viscosity",
                ),
                Slot(
                    type="FOAM_DENSITY",
                    description="PU foam density",
                ),
                Slot(
                    type="FOAM_THERM_COND",
                    description="PU foam thermal conductivity",
                ),
                Slot(
                    type="FOAM_HEIGHT",
                    description="Height profile of PU foam as time series",
                ),
                Slot(
                    type="FOAM_TEMPERATURE",
                    description="Temperature profile of PU foam as "
                                "time series",
                ),
            ),
        )
