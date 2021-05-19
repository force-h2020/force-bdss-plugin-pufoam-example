from force_bdss.api import BaseDataSourceFactory
from .cost_model import CostDataSourceModel
from .cost_data_source import CostDataSource


class CostFactory(BaseDataSourceFactory):
    def get_identifier(self):
        return "cost"

    def get_name(self):
        return "Cost Calculator"

    def get_model_class(self):
        return CostDataSourceModel

    def get_data_source_class(self):
        return CostDataSource
