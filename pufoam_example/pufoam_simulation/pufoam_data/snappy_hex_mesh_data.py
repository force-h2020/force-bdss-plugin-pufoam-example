from osp.wrappers.gmsh_wrapper.gmsh_engine import extent
from .data_format import PUFoamDataDict


library = '"caseDicts/mesh/generation/snappyHexMeshDict.cfg"'


def get_geometry_data(extent):
    min_extent = list()
    max_extent = list()
    for ax in extent.keys():
        min_extent.append(extent[ax]["min"])
        max_extent.append(extent[ax]["max"])
    return {
        'Wall': {
            'type': 'triSurfaceMesh',
            'file': '"new_surface.stl"',
        },
        'refinementBox': {
            'type': 'searchableBox',
            'min': min_extent,
            'max': max_extent
        }
    }


def get_mesh_controls(location):
    return {
        'features': [],
        'refinementSurfaces': {
            'Wall': {
                'level': [0, 0],
                'patchInfo': {'type': 'wall'}
            }
        },
        'refinementRegions': {
            'refinementBox': {
                'levels': [[[0, 0]]],
                'mode': 'inside'
            }
        },
        'locationInMesh': location,
        'allowFreeStandingZoneFaces': False
    }


snap_controls = {
    'explicitFeatureSnap': True,
    'implicitFeatureSnap': False
}

layers_controls = {
    'layers': {
        'Wall': {'nSurfaceLayers': 0}
    },
    'relativeSizes': True,
    'expansionRatio': 1.0,
    'finalLayerThickness': 0.5,
    'minThickness': 1e-3
}

write_flags = ['noRefinement']


class SnappyHexMeshData(PUFoamDataDict):
    """ Snappy Hex Mesh data file for the PUFoam simulation."""

    file_location = '"system"'
    file_name = "snappyHexMeshDict"

    def __init__(self):
        super().__init__()
        self.add_data(
            {
                "#includeEtc": library,
                "castellatedMesh": 'on',
                "snap": 'off',
                "addLayers": 'off',
                "geometry": get_geometry_data(
                    extent()
                ),
                'castellatedMeshControls': get_mesh_controls(
                    [0, 0, 0]
                ),
                'snapControls': snap_controls.copy(),
                'addLayersControls': layers_controls.copy(),
                'meshQualityControls': {},
                'writeFlags': write_flags,
                'mergeTolerance': 1e-6
            }
        )

    # def format_output(self):
    #     output = []
    #     for key, value in self.data.items():
    #         if key == 'features':
    #             output += [
    #                 f"{{file {element['file']}; level {element['level']}}}"
    #                 for element in value
    #             ]
    #
    #     return "\n".join(foam_format(self.data)) + "\n"

    def update_stl_data(self, extent, location):
        self.data.pop("geometry", None)
        self.data.pop("castellatedMeshControls", None)
        self.data["geometry"] = get_geometry_data(extent)
        self.data["castellatedMeshControls"] = get_mesh_controls(location)
