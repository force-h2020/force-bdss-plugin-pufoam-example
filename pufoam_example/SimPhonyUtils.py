#  @file SimPhonyUtils.py
#  Collection of functions related to osp-core to communicatate with
#  the OpenFoam simulation engine in on defined server
#
#  Major classes and functions:
#  CudsBuilder, CudsFinder, CudsUpdater, SimProcessor
#  OntoMetaReader, OntoCheck
#
#  @author Matthias Bueschelberger (matthias.bueschelberger@iwm.fraunhofer.de)
#  @version 0.1
#  @date 2020-07-21

# import standard libaries
import os
import tempfile

# import foam_format function from original pufoam_simulation module
from pufoam_example.pufoam_simulation.pufoam_data.data_format import (
    foam_format)

# import osp-core related sessions and libraries
from osp.core.session.transport.transport_session_client import \
    TransportSessionClient
from osp.core.session import SimWrapperSession
from osp.core.namespaces import cuba

try:
    from osp.core.namespaces import force_ofi_ontology as onto
except ImportError:
    pass


def CudsBuilder(namespace):
    """
    Function in order to automatically build cuds objects
    from a certain ontology by the use of a simple
    recursive algorithm without hard-coding their relations.
    Includes all subclasses which belong to the superclass
    of the passed namespace.

    Notes
    -----
    Ontological structure must be strictly acyclic
    and the namespaces of the entities must be unique!

    Parameters
    ----------
    namespace : str
        Namespace of the superclass

    Returns
    -------
    osp.core.cuds.Cuds
        cuds instantiated from the ontology with attached
        subclasses and their default attributes
    """
    return _recursive_add(onto[namespace])


def CudsUpdater(cuds, concept, value):
    """
    Updates a `cuds`-object by scanning its underlaying subclasses
    for a certain attribute with `concept` (e.g. "initCOH").
    The `found_cuds` resulting from the `CudsFinder` are receiving
    the new `value` (e.g. 5, 0.001, "yes", [1, 1, 1], ...).

    Parameters
    ----------
    cuds : osp.core.cuds.Cuds
        CUDS-object to be scanned for the instance holding the
        desired `concept`
    concept : str
        Key or namespace in the dictionary of an OpenFoam file (e.g. "blocks",
        "deltaH", ...)
    value : float, int, str, list
        Value which is connected to the OpenFoam-native concept (e.g. 10,
        "yes", [1, 1, 1], ...)
    """
    found_cuds = CudsFinder(cuds, concept)
    keys = found_cuds.get_attributes().keys()
    if onto["INT_VECTOR"] in keys:
        found_cuds.int_vector = value
    elif onto["FLOAT_VECTOR"] in keys:
        found_cuds.float_vector = value
    elif onto["STRING_LITERAL"] in keys:
        found_cuds.string_literal = value
    elif onto["FLOAT_VALUE"] in keys:
        found_cuds.float_value = value
    elif onto["INT_VALUE"] in keys:
        found_cuds.int_value = value
    elif onto["BOOLEAN_EXPRESSION"] in keys:
        found_cuds.boolean_expression = value


def CudsFinder(cuds, concept):
    """
    Return the disred instance with a certain `concept`-attribute
    within the passed `cuds` (e.g. "deltaH").
    The search is carried out by tracing the `path` through the
    `cuds`. This path was found during the scan through the tree
    of the related ontology.

    Parameters
    ----------
    cuds : osp.core.cuds.Cuds
        CUDS-object to be scanned for the instance holding the
        desired `concept`
    concept : str
        Key or namespace in the dictionary of an OpenFoam file (e.g. "blocks",
        "deltaH", ...)

    Returns
    -------
    osp.core.cuds.Cuds
        Instance of a certain oclass holding `concept` as object-own
        attribute found during the scan of the `cuds`
    """
    target_entity = onto[cuds.oclass.name]
    for subclass in target_entity.subclasses:
        attributes = list(subclass.attributes.values())
        attributes = [element[0].toPython() for element in attributes]
        if concept in attributes:
            path = subclass.superclasses
    for superentity in target_entity.superclasses:
        if superentity != cuba.Entity:
            path.remove(superentity)
    return _trace_path(cuds, path)


def SimProcessor(openfoam_data, model):
    """
    Write OpenFoam-native data, pass the cuds object to the server,
    run the simulation, receive the output and write the output back to
    OpenFoam-native files

    Parameters
    ----------
    openfoam_data : osp.core.cuds.Cuds
        CUDS object from the oclass of `onto["OpenFoamData"] holding the
        semantic input information being passed to the server
    model : SimPUFoamModel
        Datamodel containing traits of the host, port, commands
        and output files

    Returns
    -------
    outputfiles : list
        List class containing the paths to the output files described in the
        used ontology.
    """
    commands = model.build_commands()
    simulation = _write_file_contents(
        openfoam_data,
        commands,
        model.case_files,
        model.outputs
    )
    return _run_simulation(simulation, model.host, model.port)


def _recursive_add(base_entity):
    """
    Recursive function in order to add all subentities to the base entities

    Parameters
    ----------
    base_entity : osp.core.ontology.oclass.OntologyClass
        base entity of any level in the ontology, equals to input entity

    Returns
    -------
    osp.core.cuds.Cuds
        CUDS object of any level instantiated from the ontology with
        correlating direct subclasses of the base_entity
    """
    base_cuds = base_entity()
    for subentity in base_entity.direct_subclasses:
        if subentity.direct_subclasses:
            subcuds = _recursive_add(subentity)
            base_cuds.add(subcuds)
        else:
            base_cuds.add(subentity())
    return base_cuds


def _trace_path(target_cuds, path):
    """
    Recursively query down the path of subclasses from the
    superior `target_cuds` on, until the list is empty.
    The desired subobject at the end of the path is then
    returned

    Parameters
    ----------
    target_cuds : osp.core.cuds.Cuds
        CUDS-object to be queried for the next subclass in the `path` list
    path : list
        List of ontology classes leading to the ultimate subclass which was
        searched for during the scan in `CudsFinder`

    Returns
    -------
    osp.core.cuds.Cuds
        Instance of a certain oclass holding `concept` as object-own
        attribute found during the scan of the `cuds`
    """
    if len(path):
        path = list(path)
        subcuds = target_cuds.get(oclass=path[-1]).pop()
        path.pop(-1)
        return _trace_path(subcuds, path)
    else:
        return target_cuds


def _write_file_contents(openfoam_data, commands, case_files, outputs):
    """
    Instantiate onto["Simulation"]-class as well as the correlating
    onto["InputFiles"] and onto["OutputFiles"]. Write the content to
    be passed into the `runner`-file, build instances for the
    output-files of interest and write syntatic data for the
    simulation engine.

    Parameters
    ----------
    openfoam_data : osp.core.cuds.Cuds
        Instantiated oclass of the onto[`OpenFoamData`]
    commands : list
        List of namespaces of OpenFoam-constructors to be called to initialize
        the simulation-process (e.g. ["blockMesh", "setFields", "PUFoam"])
    case_files : str
        name of the OpenFoam-case to be used for the simulation
        (e.g. "pufoam_case")
    outputs : list
        List of paths leading to output-files of interest for post-processing
        (e.g. "postProcessing/volAverage/0/volFieldValue.dat")

    Returns
    -------
    osp.core.cuds.Cuds
        instance of onto["Simulation"]-class holding semantic as well as
        syntactic data needed for the simulation engine
    """
    simulation = onto["SIMULATION"]()
    input_files = onto["INPUT_FILES"]()
    output_files = onto["OUTPUT_FILES"]()
    case = onto["CASE"](name=case_files)
    for output in outputs:
        loc, name = os.path.split(output)
        target_file = onto["FILE"](
            name=name,
            directory=loc,
            content=str(),
            datatype="output_file"
        )
        output_files.add(target_file, rel=onto["HAS_PART"])
    runner = onto["File"](
            name="run.sh",
            directory=str(),
            content=str(),
            datatype="runner"
    )
    input_files.add(runner, rel=onto["HAS_PART"])
    for command in commands:
        runner.content += command + "\n"
    simulation.add(
        openfoam_data,
        case,
        input_files,
        output_files,
        rel=onto["HAS_PART"]
    )
    _cuds2dict(simulation)
    return simulation


def _cuds2dict(simulation):
    """
    Writing the information from the semantic cuds object
    to syntactic data for the simulation engine (using the
    `foam_format`-function already available from the BDSS plugin).
    The combined content is attached as an attribute of an extra entity
    within the root-cuds-object

    Parameters
    ----------
    simulation : osp.core.cuds.Cuds
        CUDS object from the oclass of `onto["Simulation"]` holding the
        semantic information passed to the simulation engine.

    See Also
    --------
    cuds_dict : `foam_format()` function from
                `pufoam_example.pufoam_simulation.pufoam_data.data_format`
    """
    openfoam_data = simulation.get(oclass=onto["OPEN_FOAM_DATA"]).pop()
    input_files = simulation.get(oclass=onto["INPUT_FILE"]).pop()
    for data_dict in onto["OPEN_FOAM_DATA"].direct_subclasses:
        target_dict = openfoam_data.get(oclass=data_dict).pop()
        loc = CudsFinder(target_dict, "location").string_literal
        name = CudsFinder(target_dict, "object").string_literal
        target_file = onto["FILE"](
            name=name,
            directory=loc,
            content=str(),
            datatype="input_file"
        )
        input_files.add(target_file, rel=onto["HAS_PART"])
        nested_dict = _recursive_dict_add(target_dict, dict())
        for line in foam_format(nested_dict):
            target_file.content += line + "\n"


def _recursive_dict_add(cuds, cuds_dict):
    """
    Recursive function used to build a Python dictionary or
    Python list holding the attributes of `int_value`, `int_vector`,
    `float_value`, `float_vector`, `string_literal` or `boolean_expression`
    as value and `concept` as key.
    The function also checks whether the iterated cuds subobject
    represents another nested dictionary or not.

    Parameters
    ----------
    cuds : osp.core.cuds.Cuds
        Cuds object of a certain level to be scanned for attributes of
        `concept`, `int_value`, `int_vector`, `float_value`, `float_vector`,
        `string_literal`, `boolean_expression` or `datatype`
    cuds_dict : dict, list
        Initially an empty Python list or dictionary to be passed into the
        function for storing the keys, values and sub-dictionaries

    Returns
    -------
    cuds_dict : dict
        Python dictionary holding the keys, values and/or nested dicts to write
        the OpenFoam-native dictionary as a string in one single chunk
    """
    for subcuds in cuds.iter():
        keys = subcuds.get_attributes().keys()
        datatype = subcuds.datatype
        concept = subcuds.concept
        if onto["INT_VECTOR"] in keys:
            additive = list(subcuds.int_vector)
        elif onto["FLOAT_VECTOR"] in keys:
            additive = list(subcuds.float_vector)
        elif onto["STRING_LITERAL"] in keys:
            additive = subcuds.string_literal
        elif onto["FLOAT_VALUE"] in keys:
            additive = subcuds.float_value
        elif onto["INT_VALUE"] in keys:
            additive = subcuds.int_value
        elif onto["BOOLEAN_EXPRESSION"] in keys:
            additive = subcuds.boolean_expression
        if datatype == "dict_item":
            cuds_dict[concept] = additive
        elif datatype == "list_variable":
            cuds_dict.append(additive)
        elif datatype == "dictionary":
            subcuds = _recursive_dict_add(subcuds, dict())
            cuds_dict[concept] = subcuds
        elif datatype == "function":
            subcuds = _recursive_dict_add(subcuds, dict())
            cuds_dict[concept] = [subcuds]
        elif datatype == "list":
            subcuds = _recursive_dict_add(subcuds, list())
            cuds_dict[concept] = [subcuds]
    return cuds_dict


def _run_simulation(simulation, host, port):
    """
    Exposes the CUDS object from the oclass `onto.Simulation`
    to the desired port with the `TransportSessionClient`.
    The simulation is started with `wrapper.session.run()`
    whereas the updated CUDS object with the attached output
    is received by `wrapper.get(simulation.uid)`

    Parameters
    ----------
    simulation : osp.core.cuds.Cuds
        CUDS object from the oclass of `onto.simulation` holding the semantic
        and syntactic input information being passed to the simulation engine
    host : str
        Host name the `TransportSessionClient` shall be wired to
    port : int
        Port the `TransportSessionClient` shall be wired to

    Returns
    -------
    outputfiles : list
        List class containing the paths to the output files described in the
        used ontology.
    """
    print("Sending cuds object to", host, "with uid =", simulation.uid)
    with TransportSessionClient(SimWrapperSession, host, port) as session:
        wrapper = onto["FORCE_OFI_WRAPPER"](session=session)
        wrapper.add(simulation)
        wrapper.session.run()
        simulation = wrapper.get(simulation.uid)
        return _cuds_output_to_file(simulation)


def _cuds_output_to_file(simulation):
    """
    Function to write the outputfile content within cuds object
    returned from the simulation engine into an OpenFoam-native
    file again for further processing

    Parameters
    ----------
    simulation : osp.core.cuds.Cuds
        CUDS object from the oclass of `onto.simulation` holding the semantic
        and syntactic input as well as syntactic output information from the
        simulation engine

    Returns
    -------
    paths : list
        Python list holding the local paths leading to the output-files
        of interest.
    """
    outputdir = tempfile.mkdtemp(dir=tempfile.gettempdir())
    output = simulation.get(oclass=onto["OUTPUT_FILES"]).pop()
    paths = list()
    for outputfile in output.iter():
        paths.append(outputdir)
        for arg in outputfile.directory.split('/'):
            paths[-1] = os.path.join(paths[-1], arg)
        if not os.path.exists(paths[-1]):
            os.makedirs(paths[-1])
        paths[-1] = os.path.join(paths[-1], outputfile.name)
        print(f"Writing to {paths[-1]}")
        with open(paths[-1], "w") as output_path:
            print(outputfile.content, file=output_path)
    return paths
