from force_bdss.api import BaseDataSource, Slot, DataValue


class ReactionParametersDataSource(BaseDataSource):

    def run(self, model, parameters):

        if model.input_method == 'Model':
            gelling_reaction = {
                "A_OH": model.nu_gelling,
                "E_OH": model.E_a_gelling,
                "deltaOH": model.delta_H_gelling,
                "gellingPoint": model.gelling_point
            }
            blowing_reaction = {
                "A_W": model.nu_blowing,
                "E_W": model.E_a_blowing,
                "deltaW": model.delta_H_blowing,
                "latentHeat": model.latent_heat
            }
        else:
            gelling_reaction = {
                "A_OH": parameters[0].value[0],
                "E_OH": parameters[0].value[1],
                "deltaOH": parameters[0].value[2],
                "gellingPoint": parameters[0].value[3]
            }
            blowing_reaction = {
                "A_W": parameters[1].value[0],
                "E_W": parameters[1].value[1],
                "deltaW": parameters[1].value[2],
                "latentHeat": parameters[1].value[3]
            }

        return [
            DataValue(type="REACTION", value=gelling_reaction),
            DataValue(type="REACTION", value=blowing_reaction)
        ]

    def slots(self, model):

        if model.input_method == 'Parameter':
            input_slots = (
                Slot(
                    type='VECTOR',
                    description='Vector of Gelling reaction parameters'),
                Slot(
                    type='VECTOR',
                    description='Vector of Blowing reaction parameters'),
            )
        else:
            input_slots = tuple()

        return (
            input_slots,
            (
                Slot(type="REACTION",
                     description="Parameters "
                                 "for the gelling reaction"),
                Slot(type="REACTION",
                     description="Parameters "
                                 "for the blowing reaction")
            )
        )
