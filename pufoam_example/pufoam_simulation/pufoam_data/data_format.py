import os
import collections
from copy import deepcopy

pufoam_format_data = {
    "version": 2.2,
    "format": "ascii",
    "class": "dictionary",
    "location": None,
    "object": None,
}


def value_formatting(value):
    """Formats singular values according to OpenFoam input file
    requirements"""
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def list_formatting(a_list):
    """Formats lists according to OpenFoam input file requirements"""
    return "(" + " ".join(map(str, a_list)) + ")"


def instance_of(value):
    """ Method to decide which syntactic representation should
    the `value` have in the OpenFOAM file format. We use python
    `dict` to represent the OpenFOAM `dictionary` type entry,
    and python `list, tuple` represent the OpenFOAM `list` type
    entry.

    Parameters
    ----------
    value: (list, tuple, dict)
        python object to be characterized
    Returns
    -------
    type: str
        string-format of the value type
    """
    if isinstance(value, dict):
        return "dict"
    if isinstance(value, (list, tuple)):
        return "list"
    return None


def foam_format(foam_object, level=0):
    """ Given a `foam_object` with designed structure, attempts to
    parse this object and generates a list of strings in the OpenFOAM
    file format. Two OpenFOAM entry types are supported: `dict` and `list`.
    The `dict` entry is wrapped in "{ }", the `list` entry is wrapped
    inside "( );". Low level items in a `dict` end with ";".

    Format of `foam_object`:
    We operate with a mix of nested python dicts and lists. The first level
    object must be a dictionary, whose keywords define the names of the
    OpenFOAM data groups. The lower level elements (the values of the higher
    level dictionary) can be either of type `dict`, or `(list, tuple)`.

    .. code-block:: python

        >>> d = {               # The object to be parsed
        >>>     "a" : 1,        # One line dict entry
        >>>     "b": [[2]]      # Single element list entry. In contrast to the  # noqa
        >>>                     # dict entries, OpenFOAM lists can't be one-liners. # noqa
        >>>     "c": {          # Dict entry with multiple elements
        >>>         "d": 3,
        >>>         "e": [      # List entry with multiple elements, consisting of # noqa
        >>>             [[4, 5],# of two items
        >>>             [6, 7]]
        >>>         ]
        >>>     }
        >>> }
        >>> lines = foam_format(d)
        >>> "\\n".join(lines)
        Out:
            a                             1;
            b
            (
                2
            );
            c
            {
                d                             3;
                e
                (
                    4 5
                    6 7
                );
            }
    """
    brackets = {"dict": ("{", "}\n"), "list": ("(", ");")}

    lines = []
    offset = "\t" * level

    object_type = instance_of(foam_object)

    if object_type == "dict":
        for key, value in foam_object.items():
            value_type = instance_of(value)

            if value_type is None:
                # We are inside a `dict` branch, therefore elementary entries
                # must end up with a semicolon if they are not include commands
                line = "{}{:30}{}".format(offset, key, value_formatting(value))
                if not key.startswith("#include"):
                    line += ';'
                lines.append(line)
            else:
                lines.append(f"{offset}{key}")
                lines.append(f"{offset}{brackets[value_type][0]}")
                lines += foam_format(value, level + 1)
                lines.append(f"{offset}{brackets[value_type][1]}")

    elif object_type == "list":
        inner_line = ''

        for list_entry in foam_object:
            entry_type = instance_of(list_entry)

            if entry_type is None:
                # We are inside an elementary `list` entry, therefore
                # they must be placed in one after one
                # lines.append(
                #     offset + " ".join([str(entry) for entry in list_entry])
                # )
                if not inner_line:
                    inner_line = offset
                inner_line += f"{str(list_entry)} "

            else:
                # Append any formatted singular data values in the line
                # so far before switching to container data type
                if inner_line:
                    lines.append(inner_line)

                # Nested lists are supported up to 2 layers deep
                if entry_type == 'list':
                    inner_line = offset
                    for entry in list_entry:
                        if instance_of(entry) == "list":
                            inner_line += list_formatting(entry)
                        else:
                            inner_line += str(entry)
                        inner_line += " "
                    lines.append(inner_line)
                    inner_line = ''

                if entry_type == 'dict':
                    new_lines = foam_format(list_entry, level)
                    # If inner dictionary contains file data, then this needs
                    # to be formatted inside a dictionary without a header
                    if 'file' in list_entry.keys():
                        new_lines = (
                            [f"{offset}{{"] + new_lines + [f"{offset}}}"]
                        )
                    lines += new_lines

        # Finally append any formatted singular data values
        if inner_line:
            lines.append(inner_line)

    return lines


def update_nested_dict(source, update_key, update_value):
    """ Given an `update_key` and an `update_value`, we navigate
    through a nested `source` dictionary and try to locate an element
    with the same key. If such key exists, we replace it in place.
    """
    # Can't update empty group
    if len(source) == 0:
        return False
    # If the key is in the source, update it in-place
    if update_key in source:
        source[update_key] = update_value
        return True
    # Otherwise, iterate through the items and look inside them
    else:
        for key, value in source.items():
            if isinstance(value, collections.Mapping) and value:
                # Handles the case of the DataGroup element being an
                # OpenFOAM dict
                is_updated = update_nested_dict(
                    source[key], update_key, update_value
                )
                if is_updated:
                    return True
            elif isinstance(value, (list, tuple)):
                # Handles the case of the DataGroup element being an
                # OpenFOAM list
                for element in value:
                    if isinstance(element, collections.Mapping) and element:
                        is_updated = update_nested_dict(
                            element, update_key, update_value
                        )
                        if is_updated:
                            return True
    return False


class PUFoamDataDict:
    """ This class implements PUFoam compatible representation
    of the Data Dictionaries. The data is stored in nested dict
    `data` attribute. The first data group to appear in every
    PUFoam dictionary file is file format specification.

    Attributes
    --------
    file_location: str
        Specifies the path to the PUFoam dictionary file inside the
        simulation folder. *Important*: this string must be nested
        inside an additional string because OpenFOAM expects a
        string wrapped into " ".
    """

    #: Path to the file inside the configuration directory
    file_location = '""'
    #: Name of the file associated with the PUFoam input data file
    file_name = "default"

    def __init__(self):
        self.data = {"FoamFile": pufoam_format_data}
        self.data["FoamFile"]["location"] = self.file_location
        self.data["FoamFile"]["object"] = self.file_name

    def add_data(self, other):
        self.data = {**deepcopy(self.data), **deepcopy(other)}

    @property
    def file_localpath(self):
        """ The full filename (name + path) string based on
        the values inside the first data group.
        """
        filename = ""
        location = self.file_dir
        name = self.data["FoamFile"]["object"]
        if location:
            filename = os.path.join(filename, location)
        if name:
            filename = os.path.join(filename, name)
        return filename

    @property
    def file_dir(self):
        """ The local path to file"""
        return self.data["FoamFile"]["location"].strip('"')

    def update_data(self, label, value):
        """ Attempts to update the PUFoam data by given (label, data)
        pair.
        The label can be a string of sublabels, separated by dots, e.g.
        'group.subgroup.item'. We attempt to locate the data group that
        matches this pattern and update the value of the final sublabel
        in the string.

        Returns
        --------
        update_status: bool
            True, if the update is successful. False, otherwise.
        """
        data = self.data
        *label_path, final_label = label.split(".")
        try:
            for sublabel in label_path:
                # Since we can have both `dict` and `list` type of
                # entries, we handle these two cases here
                try:
                    data = data[sublabel]
                except TypeError:
                    data = data[0][sublabel]
            if final_label in data:
                data[final_label] = value
                return True
            else:
                raise AttributeError
        except AttributeError:
            return update_nested_dict(data, label, value)

    def format_output(self):
        return "\n".join(foam_format(self.data)) + "\n"

    def write_to_file(self, path=""):

        directory = os.path.join(path, self.file_dir)
        try:
            os.makedirs(directory)
        except OSError:
            pass

        file_path = os.path.join(path, self.file_localpath)
        with open(file_path, "w") as script:
            output = self.format_output()
            script.write(output)
