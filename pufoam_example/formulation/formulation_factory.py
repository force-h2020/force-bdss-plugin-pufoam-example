from force_bdss.api import BaseDataSourceFactory

from .formulation_model import FormulationDataSourceModel
from .formulation_data_source import FormulationDataSource


class FormulationFactory(BaseDataSourceFactory):
    def get_identifier(self):
        return "formulation"

    def get_name(self):
        return "Formulation Processing"

    def get_model_class(self):
        return FormulationDataSourceModel

    def get_data_source_class(self):
        return FormulationDataSource
