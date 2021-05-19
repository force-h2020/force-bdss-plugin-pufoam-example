from force_bdss.api import BaseDataSourceFactory

from .simpufoam_data_source import SimPUFoamDataSource
from .simpufoam_model import SimPUFoamModel


class SimPUFoamFactory(BaseDataSourceFactory):
    def get_identifier(self):
        return "SimPUFoam_simulation"

    def get_name(self):
        return "SimPU(Open)Foam solver"

    def get_model_class(self):
        return SimPUFoamModel

    def get_data_source_class(self):
        return SimPUFoamDataSource
