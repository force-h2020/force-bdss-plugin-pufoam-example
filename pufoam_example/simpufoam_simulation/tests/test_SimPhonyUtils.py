from pufoam_example.SimPhonyUtils import CudsBuilder, CudsFinder, \
    CudsUpdater, _cuds_output_to_file
from osp.core import force_ofi_ontology as onto
from unittest import TestCase
from pufoam_example.pufoam_plugin import PUFoamPlugin


class test_SimPhonyUtils(TestCase):

    def setUp(self):
        self.plugin = PUFoamPlugin()
        self.factory = self.plugin.data_source_factories[-1]
        self.data_source = self.factory.create_data_source()
        self.model = self.factory.create_model()
        self.cuds = CudsBuilder("OPEN_FOAM_DATA")

    def test_Cuds_Builder_CudsUpdater_CudsFinder(self):
        new_val = 1.5
        test_dict = {
            "initCOH": "KineticsDictData",
            "A_OH": "KineticsDictData",
            "vertex_numbers": "MeshDictData",
            "maxCO": "ControlDictData"
        }
        for foam_namespace, target_namespace in test_dict.items():
            CudsUpdater(self.cuds, foam_namespace, new_val)
            found = CudsFinder(self.cuds, foam_namespace)
            keys = found.get_attributes().keys()
            if onto["FloatValue"] in keys:
                self.assertEqual(new_val, found.float_value)
            elif onto["IntValue"] in keys:
                self.assertEqual(new_val, found.int_value)
            elif onto["StringLiteral"] in keys:
                self.assertEqual(str(new_val), found.string_literal)

    def test_cuds_to_outputfile(self):
        test_str = "This is a test string"

        testfile = onto["FILE"](
            name="testfile.dat",
            directory="testfolder",
            content=str(),
            datatype="output_file"
        )
        output = onto["OUTPUT_FILES"]()
        simulation = onto["SIMULATION"]()

        output.add(testfile)
        simulation.add(output)

        testfile.content = test_str
        test_str += "\n"

        paths = _cuds_output_to_file(simulation)

        for path in paths:
            assert_str = ""
            with open(path, "r") as content:
                for line in content:
                    assert_str += line
                self.assertEqual(assert_str, test_str)
