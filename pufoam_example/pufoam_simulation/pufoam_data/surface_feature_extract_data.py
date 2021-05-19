import os

from .data_format import PUFoamDataDict


library = '"caseDicts/surface/surfaceFeatureExtractDict.cfg"'


class SurfaceFeatureExtractData(PUFoamDataDict):
    """ Mesh quality data file for the PUFoam simulation."""

    file_location = '"system"'
    file_name = "surfaceFeatureExtractDict"

    def __init__(self, file_name='new_surface.stl'):
        super().__init__()
        name, _ = os.path.splitext(file_name)
        self._file_name = file_name
        self.add_data(
            {
                f"{name}.stl": {
                    "#includeEtc": library
                },
            }
        )

    def update_mesh_file(self, file_name):
        name, extension = os.path.splitext(file_name)
        old_name, _ = os.path.splitext(self._file_name)
        self.data.pop(f"{old_name}.stl", None)

        self._file_name = name
        self.add_data(
            {
                f"{name}.stl": {
                    "#includeEtc": library
                },
            }
        )
