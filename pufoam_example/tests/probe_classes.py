from pufoam_example.chemical import Chemical
from pufoam_example.formulation import Formulation


def probe_chemicals():

    probe_polyol = Chemical(
        name="Probe Polyol",
        molecular_weight=120,
        role="Polyol",
        price=5,
        density=10,
        concentration=12,
    )

    probe_isocyante = Chemical(
        name="Probe Isocyante",
        molecular_weight=100,
        role="Isocyanate",
        price=3,
        density=20,
        concentration=100,
    )

    probe_surfactant = Chemical(
        name="Probe Surfactant",
        molecular_weight=150,
        role="Surfactant",
        price=2,
        density=5,
        concentration=5,
    )

    probe_catalyst = Chemical(
        name="Probe Catalyst",
        molecular_weight=250,
        role="Catalyst",
        price=2,
        density=2,
        concentration=0.4,
    )

    probe_blowing_agent = Chemical(
        name="CO2",
        molecular_weight=44,
        role="Blowing Agent",
        price=8,
        density=10,
        concentration=0.1,
    )

    probe_solvent = Chemical(
        name="Water",
        molecular_weight=18,
        role="Solvent",
        price=2,
        density=1,
        concentration=82,
    )

    return [
        probe_polyol,
        probe_isocyante,
        probe_solvent,
        probe_blowing_agent,
        probe_surfactant,
        probe_catalyst,
    ]


class ProbeFormulation(Formulation):
    def __init__(self, *args, **kwargs):
        super(ProbeFormulation, self).__init__(
            chemicals=probe_chemicals()
        )


class ProbeResponse:
    def __init__(self, text="Hello World"):
        self.text = text
