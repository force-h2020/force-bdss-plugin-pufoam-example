from traits.api import List, Enum

from force_bdss.api import (
    BaseCSVWriter,
    BaseCSVWriterFactory,
    BaseCSVWriterModel,
)

from pufoam_example.time_series_profiler.time_series_profiler_model import (
    TimeSeriesEvent
)

COLUMN_MAP = {'BSD': 'bsd_profile',
              'Temperature': 'temp_profile',
              'Height': 'height_profile'}


class PUFoamCSVWriterModel(BaseCSVWriterModel):
    """CSV writer model that can be adapted for the PUFoam use case"""

    #: Additional data columns to include for each MCO run
    extra_columns = List(Enum('BSD', 'Temperature', 'Height'))


class PUFoamCSVWriter(BaseCSVWriter):
    """CSV writer that can be adapted for the PUFoam use case"""

    def parse_start_event(self, event):
        """ Adds extra column names to base class header."""
        header = super().parse_start_event(event)
        return header + self.model.extra_columns

    def deliver(self, event):
        """Includes additional handling for time series data"""
        super().deliver(event)

        # Reacts to any reported time series
        if isinstance(event, TimeSeriesEvent):
            event_data = event.serialize()
            for name in self.model.extra_columns:
                ref = COLUMN_MAP[name]
                if ref in event_data:
                    # Include value for final simulation state
                    mean_value = event_data[ref][-1][-1]
                    self.row_data[name] = mean_value


class PUFoamCSVWriterFactory(BaseCSVWriterFactory):
    def get_identifier(self):
        return "pu_csv_writer"

    def get_name(self):
        return "PUFoam CSV Writer"

    def get_listener_class(self):
        return PUFoamCSVWriter

    def get_model_class(self):
        return PUFoamCSVWriterModel
