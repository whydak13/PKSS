import logging
import numpy as np
from scipy import linalg as linalg

import modelinternals


# noinspection PyPep8Naming
class Model(object):
    def __init__(self, parameters=None):
        logging.info("Created model")

        self.params = parameters if parameters is not None else Model.init_params()
        logging.info("Parameters map: %s.", self.params)

        self.sampling_rate = 0.01  # seconds
        logging.info("Using sampling rate %ss.", self.sampling_rate)
        A, B = Model.prepare_matrices(self.params)
        logging.info('Prepared matrices for continuous system.\n A=%s,\nB=%s', A, B)

        self.A, self.B = Model.make_discrete_system(A, B, self.sampling_rate)
        logging.info('Prepared matrices for discrete system.\n A=%s,\nB=%s', self.A, self.B)

        self.T_PM = 0.
        self.T_ZCO = 0.
        logging.info("Setting initial values for T_PM=%f, T_ZCO=%f", self.T_PM, self.T_ZCO)
    @staticmethod
    def init_params():
        parameters = {'M_M': 1.,
                      'c_wym': 1.,
                      'F_ZM': 1.,
                      'g_w': 1.,
                      'c_w': 1.,
                      'k_w': 1.,
                      'M_CO': 1.,
                      'F_ZCO': 1.}
        return parameters

    def tick(self, T_ZM, T_PCO):
        logging.info('Ticking with values T_ZM=%f, T_PCO=%f', T_ZM, T_PCO)
        self.T_PM, self.T_ZCO = self.tick0(self.T_PM, self.T_ZCO, T_ZM, T_PCO)
        logging.info('New state, T_PM=%f, T_ZCO=%f', self.T_PM, self.T_ZCO)

        return self.T_PM, self.T_ZCO

    def tick0(self, x1, x2, u1, u2):
        X = np.matrix([[x1], [x2]])
        U = np.matrix([[u1], [u2]])
        Xp = self.A * X + self.B * U
        return Xp.item(0), Xp.item(1)

    @staticmethod
    def prepare_matrices(params):
        c_w = params['c_w']
        F_ZM = params['F_ZM']
        c_wym = params['c_wym']
        M_CO = params['M_CO']
        F_ZCO = params['F_ZCO']
        M_M = params['M_M']
        k_w = params['k_w']
        g_w = params['g_w']

        a11 = -(k_w + F_ZM * c_w * g_w) / (M_M * c_wym)
        a12 = k_w / (M_M * c_wym)
        a21 = k_w / (M_CO * c_wym)
        a22 = -(k_w + F_ZCO * c_w * g_w) / (M_CO * c_wym)
        A = np.mat([[a11, a12], [a21, a22]])

        b11 = (F_ZM * c_w * g_w) / (M_M * c_wym)
        b22 = (F_ZCO * c_w * g_w) / (M_CO * c_wym)
        B = np.mat([[b11, 0], [0, b22]])

        return A, B

    @staticmethod
    def make_discrete_system(A, B, sampling):
        Ah = linalg.expm(A * sampling)
        Bh = modelinternals.getdiscreteb(A, B, sampling)
        return Ah, Bh


