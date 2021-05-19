from copy import deepcopy

from .data_format import PUFoamDataDict, list_formatting


def field_values_list(field_values):
    return [
        [f"volScalarFieldValue {key} {value}"]
        for key, value in field_values.items()
    ]


def format_cell_data(cell_data):

    if isinstance(cell_data, (int, float)):
        return str(cell_data)

    if isinstance(cell_data[0], (int, float)):
        return list_formatting(cell_data)

    return (
        " ".join(
            [list_formatting(data) for data in cell_data]
        )
    )


def format_regions(regions):
    return {
        "regions": [
            {
                key: {
                    **{variable: format_cell_data(data[variable])
                       for variable, value in data.items()
                       if variable != 'fieldValues'},
                    'fieldValues': field_values_list(data['fieldValues'])
                }
                for key, data in region.items()
            }
            for region in regions
        ]
    }


default_field_values = {
    "alpha.gas": 1,
    "wBA_l": 0,
    "mZero": 0,
    "mOne": 0,
    "mTwo": 0,
    "mThree": 0,
    "mFour": 0,
    "mFive": 0,
    "M0": 0,
    "M1": 0,
    "M2": 0,
    "M3": 0,
    "M4": 0,
    "M5": 0,
    "rho_foam": 1.2,
    "rho_gas": 1.2,
    "weight0": 0,
    "weight1": 0,
    "weight2": 0,
    "node0": 0,
    "node1": 0,
    "node2": 0,
    "TS": 298
}


initial_field_values = {
    "alpha.gas": 0,
    "wBA_l": 5.7e-2,
    "mZero": 1.0e+13,
    "mOne": 5.2622e-6,
    "mTwo": 2.7969e-24,
    "mThree": 1.5015e-42,
    "mFour": 8.1421e-61,
    "mFive": 4.4594e-79,
    "M0": 9.9999e12,
    "M1": 5.2622e-6,
    "M2": 2.7969e-24,
    "M3": 1.5015e-42,
    "M4": 8.1421e-61,
    "M5": 4.4594e-79,
    "rho_foam": 1100.0,
    "rho_gas": 1e-8,
    "muFoamCorr": 1e-3,
    "muMixture": 1e-3,
    "muFoam": 1e-3,
    "weight0": 5.72635e+12,
    "weight1": 4.27365e+12,
    "weight2": 3.43594e+12,
    "node0": 4.8065e-19,
    "node1": 5.8728e-19,
    "node2": 5.97756e-19,
    "TS": 300,
    "p_rgh": 1e5,
    "p": 1e5,
}


box_data = {
    "box": [[0, 0, 0], [0.1, 0.01, 0.01]],
    "fieldValues": initial_field_values
}


cylinder_data = {
    "p1": [0, 0, 0],
    "p2": [0, 0, 20],
    "radius": 150,
    "fieldValues": initial_field_values
}


class FieldsDictData(PUFoamDataDict):
    """ Fields data file for the simulation."""

    file_location = '"system"'
    file_name = "setFieldsDict"

    def __init__(self, mesh_type='Box'):
        super().__init__()
        self.add_data(
            {
                "defaultFieldValues": field_values_list(
                    default_field_values
                ),
            }
        )

        self.mesh_type = mesh_type
        self.regions = [{'boxToCell': deepcopy(box_data)},
                        {'cylinderToCell': deepcopy(cylinder_data)}]

    @property
    def mesh_type(self):
        return self._mesh_type

    @mesh_type.setter
    def mesh_type(self, value):
        if value not in ['Box', 'Cylinder']:
            raise ValueError(
                'FieldsDictData mesh_type argument must be either'
                'Box or Cylinder.')
        self._mesh_type = value

    def format_output(self):
        if self.mesh_type == 'Box':
            self.add_data(format_regions(self.regions[:1]))
        else:
            self.add_data(format_regions(self.regions[1:]))
        return super().format_output()

    def update_initial_values(self, key, value):
        self.regions[0]['boxToCell']['fieldValues'][key] = value
        self.regions[1]['cylinderToCell']['fieldValues'][key] = value

    def update_box_volume(self, extent):
        self.regions[0]['boxToCell']['box'][0] = extent[0]
        self.regions[0]['boxToCell']['box'][1] = extent[1]

    def update_cylinder_volume(self, extent):
        self.regions[1]['cylinderToCell']['radius'] = extent[0]
        self.regions[1]['cylinderToCell']['p2'][-1] = extent[1]
