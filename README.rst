**********************************
``force-bdss-plugin-pufoam-example``
**********************************

.. contents:: Table of contents


Example plugin for PUFoam use-case.
Requires a ``force-bdss`` installation, and an optional ``PUFoam`` docker image for the ``pufoam_data_source``.

This plugin is built to analyse production and fluid dynamics data for polyurethane (PU) foams.

Installation instructions
#########################

To install ``force-bdss`` and the ``force-wfmanager``, please see the following `instructions <https://github.com/force-h2020/force-bdss/blob/master/doc/source/installation.rst>`_.

Afterwards, clone the git repository:

.. code-block:: console

    git clone https://github.com/force-h2020/force-bdss-plugin-pufoam-example.git

After downloading, enter the source directory and run:

.. code-block:: console

    python -m ci install


Running via Docker
------------------

The optional docker container with ``PUFoam`` installation can be found in the Force/PUFoam container registry:
`<registry.gitlab.cc-asp.fraunhofer.de:4567/force/pufoam:latest>`_. It contains an installed version of PUFoam
running on Ubuntu with a simple Flask app API that can be used to edit input scripts and run a simulation.

Use the following command to pull the image:

.. code-block:: console

     docker pull registry.gitlab.cc-asp.fraunhofer.de:4567/force/pufoam:latest

If the machine you are running the BDSS on is able to spawn Docker containers then you can simply leave this up to
the ``PUFoamSimulation`` data source to perform for a given ``host``, ``port`` and ``simulation_directory`` in the
workflow file. It is recommended that the ``simulation_directory`` is a folder in the ``/tmp/`` directory since the
files will be modified during the MCO process. An ``output_file`` variable is also required to store the data that
will be processed by the ``PUFoamPostProcessing`` data source.

Alternatively, this image can be running in a detached container with an exposed host / port before starting the
BDSS to allow the workflow to communicate with it during the MCO execution.

.. code-block:: console

    docker run -d -p 5000:5000 -v <simulation_directory>:/shared/ registry.gitlab.cc-asp.fraunhofer.de:4567/force/pufoam:latest

Same as before, the volume share points to a ``simulation_directory`` that holds the PUFoam input files. The ``host``
and ``port`` variables provided to the ``PUFoamSimulation`` data source must then match those where the container is
exposed.

Semantic interoperability
-------------------------

Another option is offering to run the simulation via semantic interoperability on a remote server. This solution is using
the ``SimPUFoamDataSource`` which is converting the input data from the previously running data sources from the workflow into a semantic
``CUDS``-object of the `OSP-core <https://github.com/simphony/osp-core>`_.

This ``CUDS``-object is sent to the target-server via ``TransportSession`` using ``WebSockets``.

Plugin functionality
####################

This plugin implements a numerical simulation of the mold filling with physically and/or chemically blown
polyurethane foams.
A typical workflow consists of

* Chemical formulation of the experiment, such as the list of isocyanates and polyols,
  catalysts and blowing agent, and their chemical properties.
  Individual chemicals can be added to the workflow using ``ChemicalDataSource``.
  The ``FormulationDataSource`` is a container that aggregates the chemicals; the formulation can be
  passed to the numerical solver.
* Numerical solver to compute the resulting properties of the foam.
  The ``PUFoamDataSource`` implements an ``OpenFOAM 5.x`` wrapper that runs inside a ``docker`` container
  and generates the simulation results using the ``PUFoam`` source code.
  This data source is a proof of concept, and users are welcome to implement their own simulation data source
  that matches their needs.
* Simulation post-processing tools. An example post-processing is performed by the ``PUFoamPostProcessingDataSource``. This data source extracts
  the physical properties of the foam from the simulation output file, and calculates the foam mean bubble size
  and the thermal conductivity of the foam.

The plugin implements an ``MCO`` class. It performs a grid search optimization over a chemical concentrations range.
The KPIs are the total cost of the chemicals, and the final thermal conductivity of the foam.

Example cases
#############

Formulation Optimization
------------------------

An example workflow file **with** ``SimPUFoamDataSource`` can be found in ``pufoam_example/tests/fixtures/pufoam_example_simpufoam.json``.

A default workflow file **without** ``SimPUFoamDataSource`` can be found in ``pufoam_example/tests/fixtures/pufoam_example.json``.

If the Nevergrad BDSS plugin is installed, you can also run the equivalent Workflows with
a gradient-free MCO via the ``pufoam_example_simpufoam_nevergrad.json`` and ``pufoam_example_nevergrad.json`` input files

Simulation Parameterization
---------------------------

You can run the ``pufoam_reaction_parameters.json`` Workflow try to find the PUFoam gelling and blowing reaction
parameters that fit both height and temperature profiles of the ``PUFOAM_REF`` dataset. These are already known, since they
are the same as used in the ``single_point_pufoam.json``.

The MCO's progress can be viewed in the WfManager using the specially designed 'PUFoamDataView'. You can track the
fitting score of both data sets as well as inspecting the height and temperature curves for each simulation output.


Plugin limitations
##################

The ``PUFoam`` numerical solver is the core of the workflow.
This dependency results in the following limitations of the plugin:

* Simulation domain
    * A simple 2D simulation domain is implemented. Currently, it is possible to modify only the mesh resolution, but the domain size
      and shape are fixed.
    *  **Possible solution:**
       Users can define custom domains by implementing their own ``MeshData`` dictionary, or contributing a specific
       data source.
* Chemical constants
    * We are able to change the concentrations of the chemicals, but there is now obvious way to modify the chemical constants related
      to each chemical formulation.
    *  **Possible solution:**
       We expect users to implement their own models for kinetic properties, chemical constants, and chemical elements.
* Limited KPIs
    * At the moment we offer a limited number of KPIs to measure from the simulation output, based on post-processing of PUFoam.
    *  **Possible solution:**
       We expect users to implement their own Data Sources for further post processing of simulation data in order to
       calculate further KPIs.

