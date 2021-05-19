from traits.api import Float, Enum
from traitsui.api import View, Item, Group

from force_bdss.api import BaseDataSourceModel


class ReactionParametersModel(BaseDataSourceModel):

    input_method = Enum(['Model', 'Parameter'], changes_slots=True)

    nu_gelling = Float(
        desc='Pre-exponential factor for the gelling reaction in m3/mol s')

    E_a_gelling = Float(
        desc='Activation energy for the gelling reaction in J/mol')

    delta_H_gelling = Float(
        desc='Reaction enthalpy for the gelling reaction in J/mol')

    gelling_point = Float(
        desc='Gelling point of gelling reaction')

    nu_blowing = Float(
        desc='Pre-exponential factor for the blowing reaction in 1/s')

    E_a_blowing = Float(
        desc='Activation energy for the blowing reaction in J/mol')

    delta_H_blowing = Float(
        desc='Reaction enthalpy for the blowing reaction in J/mol')

    latent_heat = Float(
        desc='Latent heat of blowing agent in J/kg ')

    traits_view = View(
        Item("input_method"),
        Group(
            Item("nu_gelling"),
            Item("E_a_gelling"),
            Item("delta_H_gelling"),
            Item('gelling_point'),
            label='Gelling Reaction',
            visible_when="input_method=='Model'"
        ),
        Group(
            Item("nu_blowing"),
            Item("E_a_blowing"),
            Item("delta_H_blowing"),
            Item("latent_heat"),
            label='Blowing Reaction',
            visible_when="input_method=='Model'"
        )
    )
