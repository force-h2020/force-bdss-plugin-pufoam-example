from unittest import TestCase
from pufoam_example.simpufoam_simulation.simpufoam_model import (
    SimPUFoamCommand)


class TestSimPUFoamDataSource(TestCase):

    def setUp(self):
        self.command = SimPUFoamCommand()

    def test_build_command(self):
        self.assertEqual(
            'blockMesh',
            self.command.build_command()
        )

        self.command.log_file = 'someLog'
        self.assertEqual(
            'blockMesh >& someLog',
            self.command.build_command()
        )
