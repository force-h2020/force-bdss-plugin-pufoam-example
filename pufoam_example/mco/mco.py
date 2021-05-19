import logging
from itertools import product

from force_bdss.api import (
    BaseMCO, DataValue, RangedVectorMCOParameter
)

log = logging.getLogger(__name__)


class MCO(BaseMCO):

    def run(self, evaluator):

        model = evaluator.mco_model
        parameters = model.parameters

        log.info("Doing MCO run")

        for input_parameters in parameter_grid_generator(parameters):
            kpis = evaluator.evaluate(input_parameters)

            optimal_kpis = [DataValue(value=v) for v in kpis]
            optimal_points = [
                DataValue(value=v) for v in input_parameters
            ]

            model.notify_progress_event(
                optimal_points,
                optimal_kpis,
            )


def parameter_grid_generator(parameters):
    """Function to calculate the number of Gromacs experiments
    required and the combinations of each fragment concentrations"""

    ranges = []
    for parameter in parameters:
        if isinstance(parameter, RangedVectorMCOParameter):
            ranges.append(
                list(product(*parameter.sample_values))
            )
        else:
            ranges.append(parameter.sample_values)
    for combo in product(*ranges):
        yield combo
