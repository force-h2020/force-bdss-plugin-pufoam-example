from force_bdss.api import BaseDataSourceFactory

from .chemical_model import ChemicalDataSourceModel
from .chemical_data_source import ChemicalDataSource


class ChemicalFactory(BaseDataSourceFactory):
    def get_identifier(self):
        return "chemical"

    def get_name(self):
        return "Chemical Ingredient"

    def get_model_class(self):
        return ChemicalDataSourceModel

    def get_data_source_class(self):
        return ChemicalDataSource
