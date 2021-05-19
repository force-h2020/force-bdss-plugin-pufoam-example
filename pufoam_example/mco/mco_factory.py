from force_bdss.api import (
    BaseMCOFactory,
    BaseMCOCommunicator,
    FixedMCOParameterFactory,
    ListedMCOParameterFactory,
    RangedMCOParameterFactory,
    RangedVectorMCOParameterFactory
)

from .mco_model import MCOModel
from .mco import MCO


class MCOFactory(BaseMCOFactory):
    def get_identifier(self):
        return "pufoam_mco"

    def get_name(self):
        return "PUFoam optimizer"

    #: Returns the model class
    def get_model_class(self):
        return MCOModel

    #: Returns the optimizer class
    def get_optimizer_class(self):
        return MCO

    #: Returns the communicator class
    def get_communicator_class(self):
        return BaseMCOCommunicator

    #: Factory classes of the parameters the MCO supports.
    def get_parameter_factory_classes(self):
        return [
            FixedMCOParameterFactory,
            ListedMCOParameterFactory,
            RangedMCOParameterFactory,
            RangedVectorMCOParameterFactory
        ]
