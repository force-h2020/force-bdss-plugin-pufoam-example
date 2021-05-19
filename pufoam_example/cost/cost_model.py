from traits.api import Float

from force_bdss.api import BaseDataSourceModel


class CostDataSourceModel(BaseDataSourceModel):
    """Class that calculates the cost of chemical formulation for a
    PU foam mixture"""

    PU_volume = Float(desc='Volume of PU foam to be produced')

    threshold = Float(desc='Threshold price in $USD')
