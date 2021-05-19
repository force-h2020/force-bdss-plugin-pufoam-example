from force_bdss.api import BaseDataSourceFactory

from .mesh_builder_model import MeshBuilderDataSourceModel
from .mesh_builder_data_source import MeshBuilderDataSource


class MeshBuilderFactory(BaseDataSourceFactory):
    def get_identifier(self):
        return "mesh_builder"

    def get_name(self):
        return "OpenFOAM Mesh Builder"

    def get_model_class(self):
        return MeshBuilderDataSourceModel

    def get_data_source_class(self):
        return MeshBuilderDataSource
