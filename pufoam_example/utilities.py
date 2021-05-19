import numpy as np


def parse_data_values(data_values, key):
    """Parses a list of DataValue instances to return any
    `value` attributes where `type` attribute matches `key` argument

    Parameters
    ----------
    data_values: list of DataValue
        List of DataValues instances to parse
    key: str
        String to match for each DataValue type attribute
    """
    return [data_value.value for data_value in data_values
            if data_value.type == key]


def tanh_curve(x, x0, y0, y1, b):
    """Hyperbolic tangent curve function used to fit domain height
    trajectory
    """
    return 0.5 * ((y1 - y0) + (y1 + y0) * np.tanh((x - x0) / b))
