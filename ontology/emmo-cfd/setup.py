from setuptools import setup, find_packages
from packageinfo import VERSION, NAME


# main setup configuration class
setup(
    name=NAME,
    version=VERSION,
    author='Material Informatics Team, Fraunhofer IWM.',
    keywords='CFD, FORCE, Ontology, EMMO, Fraunhofer IWM',
    description='EMMO-based CFD ontologies',
    package_data={
        "emmo_cfd.inferred": ["*"],
        "emmo_cfd.sparql": ["*"],
        "emmo_cfd": ["*"],
    },
    python_requires=">=3.6",
    packages=find_packages(),
    include_package_data=True
)
