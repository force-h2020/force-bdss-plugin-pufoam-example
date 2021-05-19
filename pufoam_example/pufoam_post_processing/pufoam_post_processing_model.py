import numpy as np

from traits.api import Int

from force_bdss.api import BaseDataSourceModel

from pufoam_example.time_series_profiler.time_series_profiler_model import (
    TimeSeriesEvent)


class PUFoamPostProcessingModel(BaseDataSourceModel):
    """Empty class requiring no additional UI input """

    #: Number of PUFoam generated system lines in the
    #: simulation data file
    n_system_lines = Int(3, desc="Number of header lines in output file")

    def notify_time_series(self, time_series, **traits):

        if isinstance(time_series, np.ndarray):
            time_series = time_series.tolist()

        self.notify(
            TimeSeriesEvent(
                time_series=time_series,
                **traits
            )
        )
