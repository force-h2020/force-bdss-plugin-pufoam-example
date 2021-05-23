from unittest import TestCase, mock
from tempfile import TemporaryDirectory
import warnings

from force_bdss.api import DataValue

from pufoam_example.pufoam_simulation.pufoam_factory import PUFoamFactory
from pufoam_example.pufoam_simulation.pufoam_session import PUFoamSession
from osp.wrappers.gmsh_wrapper.gmsh_engine import (
    RectangularMesh, CylinderMesh, ComplexMesh
)
from pufoam_example.tests.probe_classes import (
    ProbeFormulation, ProbeResponse)
from pufoam_example.tests.fixtures.fixtures_path import get

OPEN_PATH = 'pufoam_example.pufoam_simulation.pufoam_session.open'


class TestPUFoamDataSource(TestCase):
    def setUp(self):
        self.factory = PUFoamFactory(plugin={'id': '0', 'name': 'test'})
        self.data_source = self.factory.create_data_source()
        self.model = self.factory.create_model()
        self.rectangle = RectangularMesh(
            x_length=10,
            y_length=2,
            z_length=20,
            resolution=5,
            units="cm"
        )
        self.cylinder = CylinderMesh(
            xy_radius=6,
            resolution=10,
            units="cm"
        )
        self.complex = ComplexMesh(
            source_path=get("cone.stl"),
            inside_location=[0, 0, 2.5],
            units="cm"
        )

    def test__calculate_filling_fraction(self):

        formulation = ProbeFormulation()
        formulation.chemicals = [formulation.chemicals[2]]

        self.model.use_mass = True
        foam_volume = 1e-4
        rectangle_volume = 4e-4
        cylinder_volume = 1.1304e-3
        complex_volume = 2.6180e-4

        filling_fraction = self.data_source._calculate_filling_fraction(
            self.model, formulation, self.rectangle
        )
        self.assertAlmostEqual(
            foam_volume/rectangle_volume,
            filling_fraction
        )
        filling_fraction = self.data_source._calculate_filling_fraction(
            self.model, formulation, self.cylinder
        )
        self.assertAlmostEqual(
            foam_volume/cylinder_volume,
            filling_fraction,
            delta=1e-4
        )

        self.model.foam_mass = 394.78
        self.model.foam_volume = 0.5
        foam_volume = 3.9478e-4

        filling_fraction = self.data_source._calculate_filling_fraction(
            self.model, formulation, self.complex
        )
        self.assertAlmostEqual(
            foam_volume/complex_volume,
            filling_fraction,
            delta=0.01
        )
        warnings.warn(
            "The destinction between true and apparent "
            "filling_fractions is currently not supported "
            "for ComplexMesh-geometries."
        )
        # NOTE: in case that ComplexMesh::cutoff_volume() will
        # deliver reasonable values in the future, please delete
        # the assertion before the warning and uncomment the
        # following code:
        # self.assertAlmostEqual(
        #    foam_volume/complex_volume,
        #    filling_fraction,
        #    delta=0.01
        # )

        self.model.use_mass = False

        filling_fraction = self.data_source._calculate_filling_fraction(
            self.model, formulation, self.rectangle
        )
        self.assertAlmostEqual(
            self.model.foam_volume,
            filling_fraction
        )
        filling_fraction = self.data_source._calculate_filling_fraction(
            self.model, formulation, self.cylinder
        )
        self.assertAlmostEqual(
            self.model.foam_volume,
            filling_fraction
        )
        filling_fraction = self.data_source._calculate_filling_fraction(
            self.model, formulation, self.complex
        )
        self.assertAlmostEqual(
            self.model.foam_volume,
            filling_fraction
        )

    def test__update_simulation_data(self):
        is_updated = self.data_source._update_simulation_data(
            DataValue(type="A_OH", value=2)
        )
        self.assertTrue(is_updated)
        self.assertEqual(
            2, self.data_source.data_dicts[0].data["GellingConstants"]["A_OH"]
        )

        is_updated = self.data_source._update_simulation_data(
            DataValue(type="B_OH", value=2)
        )
        self.assertFalse(is_updated)

    def test__prepare_mesh(self):

        def return_url_name(url, **kwargs):
            return ProbeResponse(text=url)

        with TemporaryDirectory() as temp_dir:
            self.model.simulation_directory = temp_dir

            self.data_source.update_mesh_data(self.rectangle, self.model)
            with mock.patch('requests.post') as mock_post, \
                    mock.patch('requests.get') as mock_get:
                mock_post.side_effect = return_url_name
                mock_get.side_effect = return_url_name
                session = PUFoamSession()
                self.assertEqual(
                    'http://0.0.0.0:5000/block_mesh',
                    self.data_source._prepare_mesh(session, self.model).text
                )

            self.data_source.update_mesh_data(self.cylinder, self.model)
            with mock.patch('requests.post') as mock_post, \
                    mock.patch('requests.get') as mock_get:
                mock_post.side_effect = return_url_name
                mock_get.side_effect = return_url_name
                session = PUFoamSession()
                self.assertEqual(
                    'http://0.0.0.0:5000/transform/constant/triSurface',
                    self.data_source._prepare_mesh(session, self.model).text
                )

            self.data_source.update_mesh_data(self.complex, self.model)
            with mock.patch('requests.post') as mock_post, \
                    mock.patch('requests.get') as mock_get:
                mock_post.side_effect = return_url_name
                mock_get.side_effect = return_url_name
                session = PUFoamSession()
                self.assertEqual(
                    'http://0.0.0.0:5000/transform/constant/triSurface',
                    self.data_source._prepare_mesh(session, self.model).text
                )

    def test_update_formulation_data(self):
        formulation = ProbeFormulation()
        data_dict = self.data_source.data_dicts[0]
        self.data_source.update_formulation_data(formulation)

        self.assertAlmostEqual(
            1118.44312716, data_dict.data["GellingConstants"]["initCOH"])
        self.assertAlmostEqual(
            11184.43127166, data_dict.data["GellingConstants"]["initCNCO"])
        self.assertAlmostEqual(
            50951.29801538, data_dict.data["GellingConstants"]["initCW"])
        self.assertAlmostEqual(
            0.00050125313,
            data_dict.data["GenericConstants"]["initBlowingAgent"])
        self.assertAlmostEqual(
            2231.29403869, data_dict.data["GenericConstants"]["rhoPolymer"])
        self.assertAlmostEqual(
            10000, data_dict.data["GenericConstants"]["rhoBlowingAgent"])

    def test_update_mesh_data(self):
        with TemporaryDirectory() as temp_dir:
            self.model.simulation_directory = temp_dir
            blockmesh = self.data_source.data_dicts[1]
            snappyhex = self.data_source.data_dicts[4]

            self.data_source.update_mesh_data(self.rectangle, self.model)
            for ax in self.rectangle.blockmesh_extent.keys():
                for direction in self.rectangle.blockmesh_extent[ax].keys():
                    self.assertEqual(
                        self.rectangle.blockmesh_extent[ax][direction],
                        blockmesh.data[ax+direction]
                    )
            self.assertListEqual(
                self.rectangle.ncells,
                blockmesh.data["blocks"][0][2]
            )
            self.assertEqual(0.01, blockmesh.data["convertToMeters"])

            self.rectangle.units = 'mm'
            self.data_source.update_mesh_data(self.rectangle, self.model)
            self.assertEqual(0.001, blockmesh.data["convertToMeters"])

            self.rectangle.units = 'm'
            self.data_source.update_mesh_data(self.rectangle, self.model)
            self.assertEqual(1.0, blockmesh.data["convertToMeters"])

            self.data_source.update_mesh_data(self.cylinder, self.model)
            box = snappyhex.data['geometry']["refinementBox"]
            loc = snappyhex.data['castellatedMeshControls']['locationInMesh']
            for num, ax in enumerate(self.cylinder.blockmesh_extent.keys()):
                for direction in self.cylinder.blockmesh_extent[ax].keys():
                    self.assertEqual(
                        self.cylinder.blockmesh_extent[ax][direction],
                        blockmesh.data[ax+direction]
                    )
                    self.assertEqual(
                        self.cylinder.stl_extent[ax][direction],
                        box[direction][num]
                    )
            self.assertListEqual(
                self.cylinder.inside_location,
                loc
            )
            self.assertListEqual(
                self.cylinder.ncells,
                blockmesh.data["blocks"][0][2]
            )
            self.assertListEqual(
                self.cylinder.ncells,
                blockmesh.data["blocks"][0][2]
            )
            self.assertEqual(0.01, blockmesh.data["convertToMeters"])

            self.cylinder.units = 'mm'
            self.data_source.update_mesh_data(self.cylinder, self.model)
            self.assertEqual(0.001, blockmesh.data["convertToMeters"])

            self.cylinder.units = 'm'
            self.data_source.update_mesh_data(self.cylinder, self.model)
            self.assertEqual(1.0, blockmesh.data["convertToMeters"])

            self.data_source.update_mesh_data(self.complex, self.model)
            box = snappyhex.data['geometry']["refinementBox"]
            loc = snappyhex.data['castellatedMeshControls']['locationInMesh']
            for num, ax in enumerate(self.complex.blockmesh_extent.keys()):
                for direction in self.complex.blockmesh_extent[ax].keys():
                    self.assertEqual(
                        self.complex.blockmesh_extent[ax][direction],
                        blockmesh.data[ax+direction]
                    )
                    self.assertEqual(
                        self.complex.stl_extent[ax][direction],
                        box[direction][num]
                    )
            self.assertListEqual(
                self.complex.inside_location,
                loc
            )
            self.assertListEqual(
                self.complex.ncells,
                blockmesh.data["blocks"][0][2]
            )
            self.assertEqual(0.01, blockmesh.data["convertToMeters"])

            self.complex.units = 'mm'
            self.data_source.update_mesh_data(self.complex, self.model)
            self.assertEqual(0.001, blockmesh.data["convertToMeters"])

            self.complex.units = 'm'
            self.data_source.update_mesh_data(self.complex, self.model)
            self.assertEqual(1.0, blockmesh.data["convertToMeters"])

    def test_update_control_data(self):
        self.model.time_steps = 100

        self.data_source.update_control_data(self.model)
        self.assertEqual(
            100, self.data_source.data_dicts[2].data["endTime"]
        )

    def test_update_fields_data(self):
        fraction = 0.2
        with TemporaryDirectory() as temp_dir:
            fields_dict = self.data_source.data_dicts[3]
            self.rectangle.write_mesh()
            self.cylinder.write_mesh(temp_dir)
            self.complex.write_mesh(temp_dir)

            self.data_source.update_fields_data(self.rectangle, fraction)
            self.assertListEqual(
                [
                    [0, 0, 0],
                    [
                        self.rectangle.length*self.rectangle.convert_to_meters,
                        self.rectangle.width*self.rectangle.convert_to_meters,
                        round(
                            self.rectangle.height *
                            self.rectangle.convert_to_meters *
                            fraction,
                            2
                        )
                    ]
                ],
                fields_dict.regions[0]['boxToCell']['box']
            )

            self.data_source.update_fields_data(self.cylinder, fraction)
            self.assertEqual(
                self.cylinder.radius*self.cylinder.convert_to_meters,
                fields_dict.regions[1]['cylinderToCell']['radius']
            )
            self.assertEqual(
                fraction*self.cylinder.height*self.cylinder.convert_to_meters,
                fields_dict.regions[1]['cylinderToCell']['p2'][-1]
            )

            self.data_source.update_fields_data(self.complex, fraction)
            self.assertListEqual(
                [
                    [
                        self.complex.stl_extent[ax]["min"]
                        for ax in ["x", "y", "z"]
                    ],
                    [
                        self.complex.stl_extent[ax]["max"]*fraction
                        if ax == "z" else self.complex.stl_extent[ax]["max"]
                        for ax in ["x", "y", "z"]]
                    ],
                fields_dict.regions[0]['boxToCell']['box']
            )

    def test_update_reaction_data(self):
        reaction_dict = self.data_source.data_dicts[0]
        mapping = {
            "A_OH": 10, "E_OH": 5, "deltaOH": 1, "gellingPoint": 2.5
        }
        self.data_source.update_reaction_data(mapping)
        self.assertEqual(
            10,
            reaction_dict.data["GellingConstants"]["A_OH"]
        )
        self.assertEqual(
            5,
            reaction_dict.data["GellingConstants"]["E_OH"]
        )
        self.assertEqual(
            1,
            reaction_dict.data["EnthalpyConstants"]["deltaOH"]
        )
        self.assertEqual(
            2.5,
            reaction_dict.data["GellingConstants"]["gellingPoint"]
        )

        mapping = {
            "A_W": 10, "E_W": 5, "deltaW": 1, "latentHeat": 2.5
        }

        self.data_source.update_reaction_data(mapping)
        self.assertEqual(
            10,
            reaction_dict.data["BlowingConstants"]["A_W"]
        )
        self.assertEqual(
            5,
            reaction_dict.data["BlowingConstants"]["E_W"]
        )
        self.assertEqual(
            1,
            reaction_dict.data["EnthalpyConstants"]["deltaW"]
        )
        self.assertEqual(
            2.5,
            reaction_dict.data["EnthalpyConstants"]["latentHeat"]
        )

    def test_verify(self):
        errors = self.model.verify()
        self.assertEqual(2, len(errors))

        self.model.foam_volume = 2
        errors = self.model.verify()
        self.assertEqual(3, len(errors))
        self.assertEqual(
            "PUFoam initial volume must be between 0 - 1",
            errors[-1].global_error
        )

        self.model.foam_volume = -1
        errors = self.model.verify()
        self.assertEqual(3, len(errors))
        self.assertEqual(
            "PUFoam initial volume must be between 0 - 1",
            errors[-1].global_error
        )

    def test_change_slots(self):
        slots = self.data_source.slots(self.model)

        self.assertEqual(4, len(slots[0]))
        self.assertEqual(1, len(slots[1]))

        self.model.input_method = 'Parameter'
        slots = self.data_source.slots(self.model)

        self.assertEqual(5, len(slots[0]))
        self.assertEqual(1, len(slots[1]))
        self.assertEqual('FILLING_FRACTION', slots[0][-1].type)

        self.model.use_mass = True
        slots = self.data_source.slots(self.model)

        self.assertEqual(5, len(slots[0]))
        self.assertEqual(1, len(slots[1]))
        self.assertEqual('MASS', slots[0][-1].type)
