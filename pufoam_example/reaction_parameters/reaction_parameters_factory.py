from force_bdss.api import BaseDataSourceFactory

from .reaction_parameters_model import ReactionParametersModel
from .reaction_parameters_data_source import ReactionParametersDataSource


class ReactionParametersFactory(BaseDataSourceFactory):
    def get_identifier(self):
        return "reaction_parameters"

    def get_name(self):
        return "Reaction Parameters"

    def get_model_class(self):
        return ReactionParametersModel

    def get_data_source_class(self):
        return ReactionParametersDataSource
