from force_bdss.api import BaseDataSourceFactory

from .time_series_profiler_data_source import TimeSeriesProfilerDataSource
from .time_series_profiler_model import TimeSeriesProfilerModel


class TimeSeriesProfilerFactory(BaseDataSourceFactory):
    def get_identifier(self):
        return "time_series_profiler"

    def get_name(self):
        return "PUFoam Data profiler"

    def get_model_class(self):
        return TimeSeriesProfilerModel

    def get_data_source_class(self):
        return TimeSeriesProfilerDataSource
