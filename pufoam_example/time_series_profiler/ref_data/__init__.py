import csv
import json
from os.path import join, dirname, abspath

import numpy as np


def get(filename):
    return join(dirpath(), filename)


def dirpath():
    return dirname(abspath(__file__))


def load_formulation(name):
    with open(get('reference_data.json')) as infile:
        ref_json = json.load(infile)
    return ref_json[name]


def load_data_set(filename):
    """Loads in a csv data file as a dictionary of
    numpy arrays
    """
    with open(filename, 'r') as input:
        reader = csv.reader(input)
        _data = [row for row in reader]

    header = _data[0]

    data = [[] for _ in range(len(header))]
    for row in _data[1:]:
        for col, value in enumerate(row):
            if value:
                data[col].append(value)

    data = {
        key: np.array(data[index], dtype=float)
        for index, key in enumerate(header)
    }
    return data
