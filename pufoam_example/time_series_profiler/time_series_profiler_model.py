import numpy as np

from traits.api import Enum, Str, List
from traitsui.api import View, Item

from force_bdss.api import (
    BaseDataSourceModel, MCORuntimeEvent, UIEventMixin)

REFERENCE_DATA_SETS = ['PUFOAM_REF']


class TimeSeriesEvent(MCORuntimeEvent, UIEventMixin):

    name = Str('time_series')

    time_series = List(maxlen=2)

    def _time_series_default(self):
        return [[], []]

    def serialize(self):
        return {self.name: self.time_series}


class TimeSeriesProfilerModel(BaseDataSourceModel):

    # Method of supplying reference data
    input_method = Enum('Model', 'Parameter', changes_slots=True)

    # Select reference data set from file
    reference_model = Enum(REFERENCE_DATA_SETS)

    traits_view = View(
        Item('input_method'),
        Item('reference_model',
             visible_when="input_method=='Model'")
    )

    def notify_time_series(self, time_series, **traits):

        if isinstance(time_series, np.ndarray):
            time_series = time_series.tolist()

        self.notify(
            TimeSeriesEvent(
                time_series=time_series,
                **traits
            )
        )
