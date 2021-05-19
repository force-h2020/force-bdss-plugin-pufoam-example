from force_bdss.api import BaseDataSourceFactory

from .pufoam_data_source import PUFoamDataSource
from .pufoam_model import PUFoamModel


class PUFoamFactory(BaseDataSourceFactory):
    def get_identifier(self):
        return "PUFoam_simulation"

    def get_name(self):
        return "PU(Open)Foam solver"

    def get_model_class(self):
        return PUFoamModel

    def get_data_source_class(self):
        return PUFoamDataSource
