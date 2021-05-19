# EMMO CFD

Extension of European Materials Modelling Ontology for Computational Fluid Dynamics

*Contact*: [Matthias Büschelberger](mailto:matthias.bueschelberger@iwm.fraunhofer.de) from the Material Informatics team, Fraunhofer IWM


## Requirements

This ontology is built on top of EMMO and some of its modules. The following table describes the version compatibility between those ontologies:

| Imported Ontologies | Version           |
| ------------------- | ----------------- |
| [EMMO](https://github.com/emmo-repo/EMMO)                | 1.0.0-beta        |


| Python Package | Minimum Version           |
| ------------------- | ----------------- |
| [`osp-core`](https://github.com/simphony/osp-core)                | 3.5.2-beta       |

## Installation

In order to install `emmo_cfd` as Python-package, please run:

```
python setup.py install
```

In order to install `emmo_cfd` as namespace in [`osp-core`](https://github.com/simphony/osp-core), please run:

```
cd emmo_cfd/inferred/
pico install <domain-of-interest>.yml
```

## Usage

For working with RDF-data, we recommend to use [Protégé](https://protege.stanford.edu/) version>=5.2.0 and the [FaCT++-Reasoner](http://owl.man.ac.uk/factplusplus/).

In a For further useage, we recommend [`osp-core`](https://github.com/simphony/osp-core) and the [`CUDSTranslator`](https://github.com/simphony/CUDSTranslator) in order to import, manipulate and export RDF-data of `emmo_cfd`.

## Related projects
- [FORCE](https://www.the-force-project.eu/); Grant agreement number: 721027 <img src="https://www.the-force-project.eu/content/dam/iwm/the-force-project/images/Force_Logo.png"  width="60">

## License

EMMO CFD with its RDF-data plus its SPARQL-queries is a Python-framework and hence is released under a BSD 3-Clause License.
