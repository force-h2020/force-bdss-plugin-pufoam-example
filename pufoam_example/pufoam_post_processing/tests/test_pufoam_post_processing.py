from unittest import TestCase

import numpy as np

from traits.api import Bool, Float
from traits.testing.unittest_tools import UnittestTools

from force_bdss.api import DataValue

from pufoam_example.pufoam_post_processing.pufoam_post_processing_factory import ( # noqa
    PUFoamPostProcessingFactory, PUFoamPostProcessingDataSource
)
from pufoam_example.tests.fixtures.fixtures_path import get
from pufoam_example.tests.dummy_classes import DummyRectangularMesh
from pufoam_example.utilities import tanh_curve


class ProbeDataSource(PUFoamPostProcessingDataSource):

    raise_error = Bool(False)

    end_height = Float(1.0)

    def calculate_filling_fraction(self, markers, data):
        """ Extract the domain average volume filling fraction from the
        simulation data.
        """
        x = np.linspace(0, 1, 50)
        kwargs = {'x0': self.end_height / 2,
                  'y0': 0,
                  'y1': self.end_height,
                  'b': 0.1}
        y = tanh_curve(x, **kwargs)
        return x, y

    def _fit_to_curve(self, x_data, y_data):
        if self.raise_error:
            raise RuntimeError
        return {'x0': 0.5,
                'y0': 0,
                'y1': y_data[-1],
                'b': 0.1}


class TestFoamBSD(TestCase, UnittestTools):

    def setUp(self):
        self.plugin = {'id': '0', 'name': 'test'}
        self.factory = PUFoamPostProcessingFactory(plugin=self.plugin)
        self.data_source = self.factory.create_data_source()
        self.model = self.factory.create_model()

        self.filepath = get("cellSource.dat")
        self.mesh = DummyRectangularMesh()
        self.markers, self.data = self.data_source.read_datafile(
            self.filepath, {"n_system_lines": self.model.n_system_lines}
        )

    def test_calculate_filling_fraction(self):
        time, fraction = self.data_source.calculate_filling_fraction(
            self.markers, self.data)
        self.assertAlmostEqual(0.100, fraction[0], 2)
        self.assertAlmostEqual(9.9037237652e-01, fraction[-1])

    def test_fit_to_curve(self):
        x_data = [0.1, 0.2, 0.3, 0.4, 1.0]
        y_data = np.tanh(x_data)

        result = self.data_source._fit_to_curve(x_data, y_data)

        self.assertAlmostEqual(0, result['x0'], 5)
        self.assertAlmostEqual(1.000, result['y1'], 5)

    def test_calculate_overpacking_fraction(self):
        data_source = ProbeDataSource(self.factory)
        overpack = data_source.calculate_overpacking_fraction(
            self.markers, self.data)
        self.assertAlmostEqual(1.0, overpack, 4)

        data_source.raise_error = True
        overpack = data_source.calculate_overpacking_fraction(
            self.markers, self.data)
        self.assertAlmostEqual(np.inf, overpack)

        # Mimic the simulation ending before the domain was filled
        data_source.end_height = 0.5
        overpack = data_source.calculate_overpacking_fraction(
            self.markers, self.data)
        self.assertAlmostEqual(0.5, overpack, 5)

    def test_calculate_viscosity(self):
        viscosity = self.data_source.calculate_viscosity(
            self.markers, self.data)
        self.assertAlmostEqual(1.09e-04, viscosity[0])
        self.assertAlmostEqual(9.962875e-04, viscosity[-1])

        # If muFoamCorr is not present in output file
        self.markers.remove('volAverage(muFoamCorr)')
        viscosity = self.data_source.calculate_viscosity(
            self.markers, self.data)
        self.assertEqual(len(self.data), len(viscosity))
        self.assertAlmostEqual(0, viscosity[0])
        self.assertAlmostEqual(0, viscosity[-1])

    def test_calculate_foam_density(self):
        rho = self.data_source.calculate_foam_density(
            self.markers, self.data)
        self.assertAlmostEqual(1.14689146e+03, rho[0])
        self.assertAlmostEqual(1.2113659e+02, rho[-1])

    def test_calculate_foam_bsd(self):
        time, bubble_size = self.data_source.calculate_foam_bsd(
            self.markers, self.data)
        self.assertAlmostEqual(1.30152456e-05, bubble_size[0])
        self.assertAlmostEqual(1.88762695e-04, bubble_size[-1])

    def test_calculate_foam_thermal_conductivity(self):
        conductivity = self.data_source.calculate_foam_thermal_conductivity(
            self.markers, self.data
        )
        self.assertAlmostEqual(223.15610147, conductivity[0])
        self.assertAlmostEqual(23.133852055, conductivity[-1])

    def test_calculate_height_profile(self):
        height_profile = self.data_source.calculate_height_profile(
            self.markers, self.data, self.mesh)
        self.assertAlmostEqual(46.0, height_profile[0][-1])
        self.assertAlmostEqual(0.19807447, height_profile[1][-1], 5)

        self.mesh.units = 'mm'
        height_profile = self.data_source.calculate_height_profile(
            self.markers, self.data, self.mesh)
        self.assertAlmostEqual(46.0, height_profile[0][-1])
        self.assertAlmostEqual(0.01980744, height_profile[1][-1], 5)

        self.mesh.units = 'm'
        height_profile = self.data_source.calculate_height_profile(
            self.markers, self.data, self.mesh)
        self.assertAlmostEqual(46.0, height_profile[0][-1])
        self.assertAlmostEqual(19.807447, height_profile[1][-1], 5)

    def test_project_height_profile(self):
        x_data = np.linspace(0, np.pi, 20)
        y_data = np.tanh(x_data)
        data_source = ProbeDataSource(self.factory)

        height_profile = data_source.projected_height_profile(
            x_data, y_data
        )
        self.assertAlmostEqual(1.0, height_profile[1][-1], 2)
        self.assertAlmostEqual(7, len(height_profile[0]))

    def test_basic_function(self):

        with self.assertTraitChanges(self.model, "event", count=3):
            res = self.data_source.run(
                self.model, [DataValue(value=self.filepath),
                             DataValue(value=self.mesh)])

        self.assertAlmostEqual(1.887626e-04, res[0].value[-1][-1])
        self.assertAlmostEqual(0.99028, res[1].value[-1], 3)
        self.assertAlmostEqual(5.786418e-02, res[2].value, 3)
        self.assertAlmostEqual(9.962875e-04, res[3].value)
        self.assertAlmostEqual(1.2113659e+02, res[4].value)
        self.assertAlmostEqual(23.13385205, res[5].value)
        self.assertAlmostEqual(46.0, res[6].value[0][-1])
        self.assertAlmostEqual(0.2, res[6].value[1][-1], 2)
        self.assertAlmostEqual(46.0, res[-1].value[0][-1])
        self.assertAlmostEqual(331.167041, res[-1].value[1][-1])

        self.assertEqual("FOAM_BSD", res[0].type)
        self.assertEqual("FILLING_FRACTION", res[1].type)
        self.assertEqual("OVERPACKING_FRACTION", res[2].type)
        self.assertEqual("FOAM_VISCOSITY", res[3].type)
        self.assertEqual("FOAM_DENSITY", res[4].type)
        self.assertEqual("FOAM_THERM_COND", res[5].type)
        self.assertEqual("FOAM_HEIGHT", res[6].type)
        self.assertEqual("FOAM_TEMPERATURE", res[-1].type)

    def test_read_data(self):
        filepath = get("cellSource.dat")
        markers, data = self.data_source.read_datafile(
            filepath, {"n_system_lines": self.model.n_system_lines}
        )
        self.assertEqual(
            [
                "Time",
                "volAverage(alpha.gas)",
                "volAverage(muFoamCorr)",
                "volAverage(mZero)",
                "volAverage(mOne)",
                "volAverage(rho_foam)",
                "volAverage(rho)",
                "volAverage(TS)",
            ],
            markers,
        )
        self.assertEqual((50, 8), data.shape)

    def test_notify_time_series(self):
        height_profile = [[], []]
        with self.assertTraitChanges(self.model, "event", count=1):
            self.model.notify_time_series(height_profile)

        with self.assertTraitChanges(self.model, "event", count=1):
            self.model.notify_time_series(
                np.array(height_profile)
            )
