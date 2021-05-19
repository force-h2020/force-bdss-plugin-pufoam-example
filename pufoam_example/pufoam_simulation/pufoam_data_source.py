import os
import subprocess
import warnings

from traits.api import List

from force_bdss.api import BaseDataSource, Slot, DataValue

from osp.wrappers.gmsh_wrapper.gmsh_engine import (
    RectangularMesh, CylinderMesh, ComplexMesh
)

from .pufoam_session import PUFoamSession
from .pufoam_data.kinetics_data import KineticData
from .pufoam_data.block_mesh_data import BlockMeshData
from .pufoam_data.snappy_hex_mesh_data import SnappyHexMeshData
from .pufoam_data.mesh_quality_data import MeshQualityData
from .pufoam_data.control_dict_data import ControlDictData
from .pufoam_data.fields_dict_data import FieldsDictData


def run_subprocess(command):
    """ Executes the `command` in subprocess"""
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()
    return stdout, stderr


class PUFoamDataSource(BaseDataSource):

    #: List of PUFoam data containers (PUFoamDataDicts)
    data_dicts = List()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.data_dicts = [
            KineticData(),
            BlockMeshData(),
            ControlDictData(),
            FieldsDictData(),
            SnappyHexMeshData(),
            MeshQualityData()
        ]

    def _calculate_filling_fraction(self, model, formulation, mesh):
        """Calculate the initial volume filling fraction, based on the foam
        mass (g), formulation density (g cm-3) and mesh volume
        """

        if model.use_mass:
            # Convert spatial units to meters
            volume = mesh.volume * mesh.convert_to_meters**3
            density = formulation.density * 1.0e6
            # Calc foam volume
            foam_volume = model.foam_mass / density
            # Calc volume fraction
            vol_frac = foam_volume / volume
        elif not model.use_mass:
            # set geometry volume
            volume = mesh.volume
            # Assume that given fraction is the true fraction
            vol_frac = model.foam_volume

        # Assume that given fraction is the true fraction
        filling_fraction = vol_frac

        if isinstance(mesh, ComplexMesh):
            warnings.warn(
                "The destinction between true and apparent "
                "filling_fractions is currently not supported "
                "for ComplexMesh-geometries."
            )
            # NOTE: in case that ComplexMesh::cutoff_volume() will
            # deliver reasonable values in the future, please delete
            # the code before the warning and uncomment the following
            # code:
            # -------------------------------
            # Express the difference between true and apparent
            # filling_fraction as a function of the apparent
            # filling_fraction
            # from scipy.optimize import minimize
            # def func(frac):
            #    return abs(
            #        vol_frac - mesh.cutoff_volume(frac)/volume
            #    )
            # This difference shall be minimized in order to get
            # the true filling_fraction
            # opt = minimize(func, x0=[vol_frac], bounds=((0, 1),))
            # assign the true filling_fraction as a result of
            # the minimization process
            # filling_fraction = opt.x[0]

        return filling_fraction

    def _prepare_mesh(self, session, model):
        """
        Prepare the mesh using Openfoam commands.
        """
        response = session.block_mesh()
        if self.data_dicts[1].data["geometryType"] != 'Rectangle':
            session.upload_mesh(
                os.path.join(
                    model.simulation_directory,
                    "new_surface.stl"
                )
            )
            response = session.transform_scale(
                self.data_dicts[1].data["convertToMeters"],
                "new_surface.stl"
            )
            session.snappy_hex_mesh()

        return response

    def update_formulation_data(self, formulation):
        """ Extracts polyol and isocyan concentrations from the formulation,
        and updates the KineticData dictionary."""

        # Update Molecular Masses
        polyol_mw = formulation.group_molecular_weight(
            formulation.polyols)
        isocyan_mw = formulation.group_molecular_weight(
            formulation.isocyanates)
        blowing_agent_mw = formulation.group_molecular_weight(
            formulation.blowing_agents)

        self._update_simulation_data(
            DataValue(type="molecularMassLiquidFoam",
                      value=polyol_mw))
        self._update_simulation_data(
            DataValue(type="molecularMassNCO",
                      value=isocyan_mw))
        self._update_simulation_data(
            DataValue(type="molecularMassBlowingAgent",
                      value=blowing_agent_mw))

        # Update Concentrations
        polyols = (
            formulation.group_molar_concentration(formulation.polyols)
        )
        isocyan = (
            formulation.group_molar_concentration(formulation.isocyanates)
        )
        # Note: functionality of water included in equivalent weight need
        # not be taken into account when calculating molar concentrations
        water = (
            formulation.group_molar_concentration(formulation.solvents)
            / sum([solvent.functionality for solvent in formulation.solvents])
        )
        # Note: blowing agent concentration is entered in as weight fraction,
        # rather than molar concentration
        blowing_agent = formulation.group_weight_fraction(
            formulation.blowing_agents)

        polyols = DataValue(type="initCOH", value=polyols)
        isocyan = DataValue(type="initCNCO", value=isocyan)
        water = DataValue(type="initCW", value=water)
        blowing_agent = DataValue(type="initBlowingAgent", value=blowing_agent)

        self._update_simulation_data(polyols)
        self._update_simulation_data(isocyan)
        self._update_simulation_data(water)
        self._update_simulation_data(blowing_agent)

        # Update Densities
        foam_density = formulation.density * 1E3
        blowing_density = formulation.group_density(
            formulation.blowing_agents) * 1E3

        self._update_simulation_data(
            DataValue(type="rhoPolymer", value=foam_density))
        self.data_dicts[3].update_initial_values('rho_foam', foam_density)
        self._update_simulation_data(
            DataValue(type="rhoBlowingAgent", value=blowing_density))

    def update_reaction_data(self, reaction_parameter):
        self.data_dicts[0].update_reaction_parameters(reaction_parameter)

    def update_mesh_data(self, mesh, model):

        if isinstance(mesh, RectangularMesh):
            geometryType = "Rectangle"
            mesh.write_mesh()
        elif isinstance(mesh, CylinderMesh):
            geometryType = "Cylinder"
            mesh.write_mesh(model.simulation_directory)
            self.data_dicts[4].update_stl_data(
                mesh.stl_extent,
                mesh.inside_location
            )
        else:
            geometryType = "Complex"
            mesh.write_mesh(model.simulation_directory)
            self.data_dicts[4].update_stl_data(
                mesh.stl_extent,
                mesh.inside_location
            )

        self.data_dicts[1].update_mesh_dimensions(mesh.blockmesh_extent)
        self.data_dicts[1].update_geometry_type(geometryType)
        self.data_dicts[1].update_mesh_resolution(mesh.ncells)
        self.data_dicts[1].update_mesh_scale(mesh.convert_to_meters)

    def update_control_data(self, model):
        self.data_dicts[2].update_end_time(model.time_steps)

    def update_fields_data(self, mesh, filling_fraction):

        mesh.filling_fraction = filling_fraction

        if isinstance(mesh, CylinderMesh):
            self.data_dicts[3].mesh_type = "Cylinder"
            self.data_dicts[3].update_cylinder_volume(mesh.filling_extent)
        else:
            self.data_dicts[3].update_box_volume(mesh.filling_extent)

    def run_simulation(self, model):
        """Run a PUFoam simulation"""

        # For the `docker` case, we either start or connect with a Docker
        # container running the PUFoam app
        if model.simulation_executable == "docker":

            # Create a PUFoam session object that handles both uploading of
            # input files and running simulation on PUFoam container
            session = PUFoamSession(
                image_name=model.image_name,
                container_name=model.container_name,
                host=model.host,
                port=model.port
            )

            # If PUFoam container is not already running, try to start one
            if not session.check_status():
                session.start_container()

            # Clear any existing simulation files
            session.clear_files()

            # Write the updated PUFoam dicts as input files to the
            # simulation directory
            for data_dict in self.data_dicts:
                session.upload_data_dict(data_dict)

            self._prepare_mesh(session, model)

            session.set_fields()

            response = session.run_pufoam()
            body = response.json()
            return body['output']
        else:
            # Currently local execution is not supported
            raise NotImplementedError()

    def run(self, model, parameters):

        # Check to see whether non-default simulation directory is
        # specified.
        if not model.output_file:
            raise ValueError(
                "File path for PUFoam output data required"
            )

        for parameter in parameters:

            if parameter.type == "FORMULATION":
                # assign formulation data
                formulation = parameter.value

            if parameter.type == "REACTION":
                # assign reaction parameters
                reaction = parameter.value

            if parameter.type == "MESH":
                # assign mesh instance
                mesh = parameter.value

            if parameter.type == "FILLING_FRACTION":
                # Assign the model filling fraction if available as an
                # MCO parameter
                filling_fraction = parameter.value

        # If foam mass is used to define initial conditions, calculate the
        # equivalent filling fraction of mesh
        if model.input_method == 'Model':
            filling_fraction = self._calculate_filling_fraction(
                model, formulation, mesh
            )

        # Update the PUFoam dicts based on the simulation parameters
        self.update_control_data(model)
        self.update_formulation_data(formulation)
        self.update_reaction_data(reaction)
        self.update_mesh_data(mesh, model)
        self.update_fields_data(mesh, filling_fraction)

        # Run the PUFoam simulation and save output
        results = self.run_simulation(model)

        file_path = os.path.join(
            model.simulation_directory, model.output_file
        )
        with open(file_path, 'w') as outfile:
            outfile.write(results)

        return [DataValue(type="SIMULATION_OUTPUT", value=file_path)]

    def slots(self, model):
        """ These slots are placeholders and need to be updated"""
        chemical_slots = (
            Slot(
                description="PU formulation for a simulation",
                type="FORMULATION",
            ),
        )

        reaction_parameter_slots = (
            Slot(description="Gelling reaction parameters", type="REACTION"),
            Slot(description="Blowing reaction parameters", type="REACTION"),
        )

        mesh_slot = (Slot(description="Simulation domain", type="MESH"),)

        if model.input_method == 'Parameter':
            if model.use_mass:
                mesh_slot += (Slot(
                    description="Initial foam mass",
                    type="MASS"),)
            else:
                mesh_slot += (Slot(
                    description="Initial foam filling fraction",
                    type="FILLING_FRACTION"),)

        return (
            chemical_slots + reaction_parameter_slots + mesh_slot,
            (
                Slot(
                    description="Simulation output data",
                    type="SIMULATION_OUTPUT",
                ),
            ),
        )

    def _update_simulation_data(self, parameter):
        """ A naive way to update data dictionaries from
        parameters. This updates only the existing entries,
        and assumes that the data 'labels' (keys) are unique.
        """
        for data_dict in self.data_dicts:
            is_updated = data_dict.update_data(parameter.type, parameter.value)
            if is_updated:
                return True
        return False
