from .data_format import PUFoamDataDict


library = '"caseDicts/mesh/generation/meshQualityDict.cfg"'


class MeshQualityData(PUFoamDataDict):
    """ Mesh quality data file for the PUFoam simulation."""

    file_location = '"system"'
    file_name = "meshQualityDict"

    def __init__(self):
        super().__init__()
        self.add_data(
            {
                "#includeEtc": library,
            }
        )
