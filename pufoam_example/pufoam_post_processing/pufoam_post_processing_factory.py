from force_bdss.api import BaseDataSourceFactory

from .pufoam_post_processing_model import PUFoamPostProcessingModel
from .pufoam_post_processing_data_source import PUFoamPostProcessingDataSource


class PUFoamPostProcessingFactory(BaseDataSourceFactory):
    def get_identifier(self):
        return "foam_post_processing"

    def get_name(self):
        return "Post-processing PUFoam simulation data"

    def get_description(self):
        return (
            r"""
            Calculates volume averaged properties of the simulation cell from
            the raw PUFoam output data. This raw data includes the zero and
            first order BSD moments \(m_0, m_1\), as well as the bubble and
            liquid densities \(\rho_b, \rho_{PU}\) of the final timestep:

            <ul>
            <li>Bubble size diameter (μm)
                $$d_b = \left(\frac{m_1}{m_0}\frac{6}{\pi}\right)^{1/3}$$
            </li>
            <li>Foam density (kg m<sup>-3</sup>)
                $$\rho_f = \frac{\rho_b m_1 + \rho_{PU}}{1+m_1}$$
            </li>
            <li>Foam thermal conductivity (mW m<sup>-1</sup> K<sup>-1</sup>)
                $$\lambda =
                \begin{cases}
                    8.7006\times 10^{-8}\rho_f^2 + 8.4674\times 10^{-5}\rho_f
                    + 1.16\times 10^{-2} & \rho_f > 48 \\
                    9.3738\times 10^{-6}\rho_f^2 - 7.3511\times 10^{-4}\rho_f
                    + 2.965\times 10^{-2} & \rho_f < 48 \\
                \end{cases}$$
            </li>
            </ul>

            Additionally, the following properties are extracted directly from
            PUFoam output data:

            <ul>
            <li>Filling fraction of the domain</li>
            <li>Foam viscosity (Pa s)</li>
            </li>
            </ul>

            All of which are derived from M. Karimi, H. Droghetti,
            D.L. Marchisio, <em>"PUFoam: A novel open-source CFD solver for the
            simulation of polyurethane foams"</em> (2017)
            """
        )

    def get_model_class(self):
        return PUFoamPostProcessingModel

    def get_data_source_class(self):
        return PUFoamPostProcessingDataSource
