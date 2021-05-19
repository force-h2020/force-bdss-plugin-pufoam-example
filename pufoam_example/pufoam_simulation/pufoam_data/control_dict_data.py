from .data_format import PUFoamDataDict

volume_average_function = {
    "type": "volFieldValue",
    "functionObjectLibs": '("libfieldFunctionObjects.so")',
    "log": "true",
    "valueOutput": "false",
    "source": "all",
    "operation": "volAverage",
    "writeControl": "outputTime",
    "writeInterval": 1,
    "writeFields": "true",
    "fields": [["alpha.gas"], ["muFoamCorr"], ["mZero"],
               ["mOne"], ["rho_foam"], ["rho"], ["TS"]],
}


class ControlDictData(PUFoamDataDict):
    """ Kinetics data file for the simulation."""

    file_location = '"system"'
    file_name = "controlDict"

    def __init__(self):
        super().__init__()
        self.add_data(
            {
                "application": "QmomKinetics",
                "startFrom": "startTime",
                "startTime": 0,
                "endTime": 50,
                "deltaT": 0.25,
                "writeControl": "adjustableRunTime",
                "writeInterval": 1,
                "purgeWrite": 0,
                "writeFormat": "ascii",
                "writePrecision": 8,
                "writeCompression": "uncompressed",
                "timeFormat": "general",
                "timePrecision": 8,
                "runTimeModifiable": "yes",
                "adjustTimeStep": "yes",
                "maxCo": 0.2,
                "maxAlphaCo": 0.1,
                "maxDeltaT": 0.25,
                "functions": {"volAverage": volume_average_function},
            }
        )

    def update_end_time(self, time):
        self.data["endTime"] = time
