from .data_format import PUFoamDataDict

domain_vertices = [
    [["$xmin", "$ymin", "$zmin"]],
    [["$xmax", "$ymin", "$zmin"]],
    [["$xmax", "$ymax", "$zmin"]],
    [["$xmin", "$ymax", "$zmin"]],
    [["$xmin", "$ymin", "$zmax"]],
    [["$xmax", "$ymin", "$zmax"]],
    [["$xmax", "$ymax", "$zmax"]],
    [["$xmin", "$ymax", "$zmax"]],
]

blocks = [["hex", list(range(8)), [10, 20, 40], "simpleGrading", [1, 1, 1]]]

edges = []

wall_data = {
    "type": "wall",
    "faces": [[[0, 4, 7, 3]], [[1, 2, 6, 5]], [[0, 1, 5, 4]]],
}
front_back_data = {"type": "empty", "faces": [[[5, 6, 7, 4]], [[0, 3, 2, 1]]]}

atmosphere_data = {"type": "patch", "faces": [[[6, 2, 3, 7]]]}

boundary_data = [
    {
        "Wall": wall_data,
        "frontAndBack": front_back_data,
        "atmosphere": atmosphere_data,
    }
]

merge_patches_data = []


class BlockMeshData(PUFoamDataDict):
    """ Mesh data file for the PUFoam simulation."""

    file_location = '"system"'
    file_name = "blockMeshDict"

    def __init__(self):
        super().__init__()
        self.add_data(
            {
                "convertToMeters": 0.01,
                "xmin": 0,
                "xmax": 5,
                "ymin": 0,
                "ymax": 10,
                "zmin": 0,
                "zmax": 20,
                "geometryType": "Rectangle",
                "vertices": domain_vertices.copy(),
                "blocks": blocks.copy(),
                "edges": edges.copy(),
                "boundary": boundary_data.copy(),
                "mergePatchPairs": merge_patches_data.copy(),
            }
        )

    def update_mesh_resolution(self, resolution):
        self.data["blocks"][0][2][:] = resolution

    def update_mesh_dimensions(self, extent):
        for ax in extent.keys():
            for direction in extent[ax].keys():
                self.data[ax+direction] = extent[ax][direction]

    def update_mesh_scale(self, scale):
        self.data["convertToMeters"] = scale

    def update_geometry_type(self, type):
        self.data["geometryType"] = type
