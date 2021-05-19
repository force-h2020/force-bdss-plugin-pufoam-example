from force_bdss.api import BaseExtensionPlugin, plugin_id

from pufoam_example.pufoam_post_processing.pufoam_post_processing_factory import (  # noqa: 501
    PUFoamPostProcessingFactory
)
from pufoam_example.chemical.chemical_factory import ChemicalFactory
from pufoam_example.cost.cost_factory import CostFactory
from pufoam_example.formulation.formulation_factory import (
    FormulationFactory
)
from pufoam_example.csv_writer.pufoam_csv_writer import PUFoamCSVWriterFactory
from pufoam_example.mco.mco_factory import MCOFactory
from pufoam_example.mesh_builder.mesh_builder_factory import (
    MeshBuilderFactory
)
from pufoam_example.time_series_profiler.time_series_profiler_factory import (
    TimeSeriesProfilerFactory
)
from pufoam_example.reaction_parameters.reaction_parameters_factory import (
    ReactionParametersFactory
)
from pufoam_example.pufoam_simulation.pufoam_factory import PUFoamFactory
from pufoam_example.simpufoam_simulation.simpufoam_factory import (
    SimPUFoamFactory)

PLUGIN_VERSION = 0


class PUFoamPlugin(BaseExtensionPlugin):
    """This is an example plugin for the BDSS investigating polyurethane
    (PU) foams.
    """

    id = plugin_id("pufoam", "example", PLUGIN_VERSION)

    def get_name(self):
        return "PUFoam Example"

    def get_description(self):
        return (
            "An example plugin to investigate"
            "properties of polyurethane foams")

    def get_version(self):
        return PLUGIN_VERSION

    def get_factory_classes(self):
        return [
            MCOFactory,
            ChemicalFactory,
            FormulationFactory,
            MeshBuilderFactory,
            ReactionParametersFactory,
            CostFactory,
            PUFoamPostProcessingFactory,
            PUFoamFactory,
            SimPUFoamFactory,
            PUFoamCSVWriterFactory,
            TimeSeriesProfilerFactory
        ]

    def get_data_views(self):
        # This import is only needed if data views are ever requested
        from pufoam_example.data_view.pufoam_data_view import PUFoamDataView
        return [
            PUFoamDataView
        ]
